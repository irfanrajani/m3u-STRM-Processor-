from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import requests
import logging
from pathlib import Path
import re
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class M3URequest(BaseModel):
    m3u_url: str
    output_path: str
    merge_duplicates: bool = True
    prefer_quality: str = "best"  # "best", "hd", "sd", "all"
    organize_by_category: bool = False
    fuzzy_match_threshold: float = 0.85

class Channel(BaseModel):
    name: str
    url: str
    quality: str = "unknown"
    category: str = "uncategorized"
    group: Optional[str] = None

def extract_quality(name: str) -> str:
    """Detect quality from channel name."""
    name_upper = name.upper()
    if any(q in name_upper for q in ['4K', 'UHD', '2160P']):
        return '4k'
    elif any(q in name_upper for q in ['FHD', '1080P', 'FULL HD']):
        return 'fhd'
    elif any(q in name_upper for q in ['HD', '720P']):
        return 'hd'
    elif any(q in name_upper for q in ['SD', '480P', '360P']):
        return 'sd'
    return 'unknown'

def quality_score(quality: str) -> int:
    """Score quality for sorting (higher is better)."""
    scores = {'4k': 4, 'fhd': 3, 'hd': 2, 'sd': 1, 'unknown': 0}
    return scores.get(quality, 0)

def normalize_name(name: str) -> str:
    """Remove quality indicators and extra whitespace."""
    normalized = re.sub(r'\s*(4K|UHD|FHD|HD|SD|1080P|720P|480P|360P|2160P)\s*', ' ', name, flags=re.IGNORECASE)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def parse_m3u(content: str) -> List[Channel]:
    """Parse M3U content into channel objects."""
    channels = []
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    i = 0
    
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # Extract channel info
            name = None
            group = None
            
            # Try to extract group-title
            group_match = re.search(r'group-title="([^"]+)"', line)
            if group_match:
                group = group_match.group(1)
            
            # Extract channel name (after last comma)
            if "," in line:
                name = line.split(",", 1)[1].strip()
            else:
                name = f"Channel {len(channels) + 1}"
            
            # Find the URL (next non-comment line)
            url = None
            j = i + 1
            while j < len(lines):
                candidate = lines[j]
                if not candidate.startswith("#"):
                    url = candidate
                    break
                j += 1
            
            if url:
                quality = extract_quality(name)
                channels.append(Channel(
                    name=name,
                    url=url,
                    quality=quality,
                    category=group or "uncategorized",
                    group=group
                ))
                i = j
            else:
                logger.warning("Missing URL for channel '%s'", name)
        i += 1
    
    return channels

def deduplicate_by_url(channels: List[Channel]) -> List[Channel]:
    """Remove channels with duplicate URLs."""
    seen_urls = set()
    unique = []
    
    for channel in channels:
        if channel.url not in seen_urls:
            seen_urls.add(channel.url)
            unique.append(channel)
        else:
            logger.info("Skipping duplicate URL: %s (%s)", channel.name, channel.url[:50])
    
    return unique

def merge_quality_variants(channels: List[Channel], prefer_quality: str, fuzzy_threshold: float) -> List[Channel]:
    """Merge channels that are quality variants of the same channel."""
    groups = {}
    
    for channel in channels:
        base_name = normalize_name(channel.name)
        
        # Try to find similar existing group
        matched_group = None
        for existing_base in groups.keys():
            similarity = SequenceMatcher(None, base_name.lower(), existing_base.lower()).ratio()
            if similarity >= fuzzy_threshold:
                matched_group = existing_base
                break
        
        if matched_group:
            groups[matched_group].append(channel)
        else:
            groups[base_name] = [channel]
    
    # Select best variant from each group
    merged = []
    for base_name, variants in groups.items():
        if len(variants) == 1:
            merged.append(variants[0])
        else:
            logger.info("Found %d variants of '%s': %s", 
                       len(variants), base_name, 
                       [f"{v.name} ({v.quality})" for v in variants])
            
            if prefer_quality == "all":
                # Keep all variants
                merged.extend(variants)
            elif prefer_quality == "best":
                # Keep highest quality
                best = max(variants, key=lambda c: quality_score(c.quality))
                merged.append(best)
            else:
                # Keep specific quality if available, otherwise best
                matching = [v for v in variants if v.quality == prefer_quality]
                if matching:
                    merged.append(matching[0])
                else:
                    best = max(variants, key=lambda c: quality_score(c.quality))
                    merged.append(best)
    
    return merged

def create_strm_files(channels: List[Channel], output_path: str, organize_by_category: bool):
    """Create STRM files from channel list."""
    base_path = Path("/output").resolve()
    safe_output_path = (base_path / output_path).resolve()
    
    if base_path != safe_output_path and base_path not in safe_output_path.parents:
        logger.error("Attempted directory traversal: %s", output_path)
        raise ValueError("Invalid output path specified.")
    
    safe_output_path.mkdir(parents=True, exist_ok=True)
    
    # Track filenames to handle collisions
    filename_counts = {}
    created_count = 0
    
    for channel in channels:
        # Determine output directory
        if organize_by_category and channel.category != "uncategorized":
            category_path = safe_output_path / channel.category
            category_path.mkdir(parents=True, exist_ok=True)
            target_dir = category_path
        else:
            target_dir = safe_output_path
        
        # Sanitize filename
        sanitized_name = "".join(c for c in channel.name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if not sanitized_name:
            sanitized_name = f"channel_{created_count + 1}"
        
        # Handle filename collisions
        base_filename = sanitized_name
        counter = 1
        while sanitized_name in filename_counts:
            sanitized_name = f"{base_filename}-{counter}"
            counter += 1
        
        filename_counts[sanitized_name] = True
        file_path = target_dir / f"{sanitized_name}.strm"
        
        try:
            file_path.write_text(channel.url + "\n", encoding="utf-8")
            created_count += 1
            logger.info("Created: %s → %s", sanitized_name, channel.url[:60])
        except OSError as exc:
            logger.error("Could not write %s: %s", file_path, exc)
    
    return created_count

@app.post("/process-m3u/")
async def process_m3u(request: M3URequest):
    """Process M3U playlist and create STRM files."""
    logger.info("Processing M3U from URL: %s", request.m3u_url)
    logger.info("Options: merge=%s, quality=%s, organize=%s, fuzzy=%.2f",
               request.merge_duplicates, request.prefer_quality, 
               request.organize_by_category, request.fuzzy_match_threshold)
    
    try:
        # Fetch M3U
        response = requests.get(request.m3u_url, timeout=30)
        response.raise_for_status()
        
        # Parse channels
        channels = parse_m3u(response.text)
        logger.info("Parsed %d channels from M3U", len(channels))
        
        # Remove duplicate URLs
        channels = deduplicate_by_url(channels)
        logger.info("After URL deduplication: %d channels", len(channels))
        
        # Merge quality variants if requested
        if request.merge_duplicates:
            channels = merge_quality_variants(
                channels, 
                request.prefer_quality,
                request.fuzzy_match_threshold
            )
            logger.info("After merging variants: %d channels", len(channels))
        
        # Create STRM files
        created_count = create_strm_files(
            channels, 
            request.output_path,
            request.organize_by_category
        )
        
        message = f"Successfully created {created_count} STRM files"
        if request.merge_duplicates:
            message += f" (merged from {len(parse_m3u(response.text))} original entries)"
        
        logger.info(message)
        return {
            "message": message,
            "channels_created": created_count,
            "duplicates_removed": len(parse_m3u(response.text)) - created_count if request.merge_duplicates else 0
        }
        
    except requests.exceptions.RequestException as exc:
        logger.error("Error fetching M3U file: %s", exc)
        raise HTTPException(status_code=400, detail=f"Error fetching M3U file: {exc}")
    except ValueError as exc:
        logger.error("Path validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("An unexpected error occurred: %s", exc)
        raise HTTPException(status_code=500, detail=f"An error occurred: {exc}")

# Mount static files - must be after all API routes
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")