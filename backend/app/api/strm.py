from __future__ import annotations

import os
import re
import math
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter()

QUALITY_ORDER = ["4K", "UHD", "FHD", "HD", "SD", "LOW"]

class ProcessRequest(BaseModel):
    m3u_url: str = Field(..., description="Remote or local M3U URL/path")
    output_path: str = Field("channels", description="Subdirectory under OUTPUT_DIR")
    merge_duplicates: bool = True
    prefer_quality: str = Field(settings.DEFAULT_QUALITY_PREFERENCE, regex="^(best|4k|hd|sd|all)$")
    organize_by_category: bool = False
    fuzzy_match_threshold: float = Field(settings.DEFAULT_FUZZY_THRESHOLD, ge=0.0, le=1.0)
    clean_output_first: bool = False

class ProcessResult(BaseModel):
    message: str
    channels_created: int
    duplicates_removed: int
    categories_used: int
    output_dir: str

def fetch_m3u(url: str) -> List[str]:
    import requests
    try:
        if url.startswith("http://") or url.startswith("https://"):
            r = requests.get(url, timeout=25)
            r.raise_for_status()
            return r.text.splitlines()
        else:
            return Path(url).read_text().splitlines()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load M3U: {e}")

def sanitize_filename(name: str) -> str:
    name = name.strip().replace("/", "_")
    name = re.sub(r"[^\w\s\.-]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()[:180]

def extract_entries(lines: List[str]) -> List[Dict[str, str]]:
    entries = []
    current_meta = None
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF:"):
            current_meta = line
        elif current_meta and line and not line.startswith("#"):
            name_match = re.search(r"#EXTINF:-?\d+.*?,(.*)$", current_meta)
            group_match = re.search(r'group-title="([^"]+)"', current_meta)
            name = name_match.group(1).strip() if name_match else "Unknown"
            group = group_match.group(1).strip() if group_match else "Uncategorized"
            entries.append({"name": name, "group": group, "url": line})
            current_meta = None
    return entries

def classify_quality(name: str, url: str) -> str:
    s = f"{name} {url}".lower()
    if "4k" in s or "2160" in s or "uhd" in s: return "4K"
    if "1080" in s or "fhd" in s: return "FHD"
    if "720" in s or "hd" in s: return "HD"
    if "480" in s or "sd" in s: return "SD"
    return "LOW"

def similarity(a: str, b: str) -> float:
    import difflib
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def pick_best(variants: List[Dict[str, str]]) -> Dict[str, str]:
    ranked = sorted(variants, key=lambda v: QUALITY_ORDER.index(v["quality"]) if v["quality"] in QUALITY_ORDER else math.inf)
    return ranked[0]

@router.post("/process-m3u/", response_model=ProcessResult)
def process_m3u(payload: ProcessRequest):
    lines = fetch_m3u(payload.m3u_url)
    raw_entries = extract_entries(lines)
    if not raw_entries:
        raise HTTPException(status_code=400, detail="No entries found in M3U")

    # Annotate quality
    for e in raw_entries:
        e["quality"] = classify_quality(e["name"], e["url"])

    # Merge logic
    merged: Dict[str, List[Dict[str, str]]] = {}
    if payload.merge_duplicates:
        for entry in raw_entries:
            placed = False
            for key in list(merged.keys()):
                if similarity(entry["name"], key) >= payload.fuzzy_match_threshold:
                    merged[key].append(entry)
                    placed = True
                    break
            if not placed:
                merged[entry["name"]] = [entry]
    else:
        for entry in raw_entries:
            merged[entry["name"]] = [entry]

    output_root = Path(settings.OUTPUT_DIR) / payload.output_path
    if payload.clean_output_first and output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    written = 0
    duplicates_removed = 0
    category_set = set()

    for canonical, variants in merged.items():
        category_set.update([v["group"] for v in variants])
        chosen_variants: List[Dict[str, str]]
        if payload.prefer_quality == "all" or not payload.merge_duplicates:
            chosen_variants = variants
        else:
            # Filter by requested tier if specified
            if payload.prefer_quality in ("4k", "hd", "sd"):
                tier_map = {"4k": "4K", "hd": "HD", "sd": "SD"}
                filtered = [v for v in variants if v["quality"].lower() == tier_map[payload.prefer_quality].lower()]
                if filtered:
                    chosen_variants = [pick_best(filtered)]
                else:
                    chosen_variants = [pick_best(variants)]
            else:  # best
                chosen_variants = [pick_best(variants)]
            duplicates_removed += max(0, len(variants) - len(chosen_variants))

        for v in chosen_variants:
            safe_name = sanitize_filename(canonical)
            target_dir = output_root
            if payload.organize_by_category:
                cat = sanitize_filename(v["group"])
                target_dir = output_root / cat
                target_dir.mkdir(parents=True, exist_ok=True)
            strm_path = target_dir / f"{safe_name}.strm"
            strm_path.write_text(v["url"])
            written += 1

    return ProcessResult(
        message=f"Successfully created {written} STRM files (merged from {len(raw_entries)} original entries)",
        channels_created=written,
        duplicates_removed=duplicates_removed,
        categories_used=len(category_set),
        output_dir=str(output_root)
    )
