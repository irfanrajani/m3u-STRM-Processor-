from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class M3URequest(BaseModel):
    m3u_url: str
    output_path: str

def parse_m3u(content):
    playlist = []
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            name = line.split(",", 1)[1].strip() if "," in line else f"Channel {len(playlist) + 1}"
            url = None
            j = i + 1
            while j < len(lines):
                candidate = lines[j]
                if candidate.startswith("#"):
                    j += 1
                    continue
                url = candidate
                break
            if url:
                playlist.append({"name": name, "url": url})
                i = j
            else:
                logger.warning("Missing URL for channel '%s'", name)
        i += 1
    return playlist

def create_strm_files(playlist, output_path):
    base_path = Path("/output").resolve()
    safe_output_path = (base_path / output_path).resolve()
    if base_path != safe_output_path and base_path not in safe_output_path.parents:
        logger.error("Attempted directory traversal: %s", output_path)
        raise ValueError("Invalid output path specified.")
    safe_output_path.mkdir(parents=True, exist_ok=True)

    for idx, item in enumerate(playlist, start=1):
        if 'name' not in item or 'url' not in item:
            continue
        sanitized_name = "".join(c for c in item['name'] if c.isalnum() or c in (' ', '.', '_')).rstrip()
        if not sanitized_name:
            sanitized_name = f"channel_{idx}"
        filename = safe_output_path / f"{sanitized_name}.strm"
        try:
            filename.write_text(item['url'] + "\n", encoding="utf-8")
        except OSError as exc:
            logger.error("Could not write %s: %s", filename, exc)


@app.post("/process-m3u/")
async def process_m3u(request: M3URequest):
    logger.info(f"Processing M3U from URL: {request.m3u_url}")
    try:
        response = requests.get(request.m3u_url, timeout=30)
        response.raise_for_status()
        playlist = parse_m3u(response.text)
        create_strm_files(playlist, request.output_path)
        
        logger.info("Successfully created STRM files.")
        return {"message": "STRM files created successfully"}
    except requests.exceptions.RequestException as exc:
        logger.error("Error fetching M3U file: %s", exc)
        raise HTTPException(status_code=400, detail=f"Error fetching M3U file: {exc}")
    except ValueError as exc:
        logger.error("Path validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("An unexpected error occurred: %s", exc)
        raise HTTPException(status_code=500, detail=f"An error occurred: {exc}")

# Mount the static files directory for the frontend
# This must be after all API routes
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")