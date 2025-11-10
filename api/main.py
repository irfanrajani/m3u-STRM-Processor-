from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    lines = content.splitlines()
    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            name, url = line.split(",", 1)
            playlist.append({'name': name, 'url': url})
    return playlist

def create_strm_files(playlist, output_path):
    base_path = Path("/output").resolve()
    safe_output_path = (base_path / output_path).resolve()
    if base_path != safe_output_path and base_path not in safe_output_path.parents:
        logger.error("Attempted directory traversal: %s", output_path)
        raise ValueError("Invalid output path specified.")
    safe_output_path.mkdir(parents=True, exist_ok=True)

    for item in playlist:
        if 'name' not in item or 'url' not in item:
            continue
        sanitized_name = "".join(c for c in item['name'] if c.isalnum() or c in (' ', '.', '_')).rstrip()
        filename = safe_output_path / f"{sanitized_name}.strm"
        try:
            filename.write_text(item['url'])
        except OSError as exc:
            logger.error("Could not write %s: %s", filename, exc)


@app.post("/process-m3u/")
async def process_m3u(request: M3URequest):
    logger.info(f"Processing M3U from URL: {request.m3u_url}")
    try:
        response = requests.get(request.m3u_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
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