from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import logging

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
    # Secure the output path
    # This prevents directory traversal attacks (e.g., ../../)
    # It resolves the path and ensures it's within the intended base directory.
    # Assuming '/output' inside the container is the base for all user-writable content.
    base_path = os.path.abspath("/output")
    safe_output_path = os.path.abspath(os.path.join(base_path, output_path))

    if not safe_output_path.startswith(base_path):
        logger.error(f"Attempted directory traversal: {output_path}")
        raise ValueError("Invalid output path specified.")

    if not os.path.exists(safe_output_path):
        os.makedirs(safe_output_path)
        
    for item in playlist:
        if 'name' not in item or 'url' not in item:
            continue
            
        # Sanitize channel name to create a valid filename
        sanitized_name = "".join(c for c in item['name'] if c.isalnum() or c in (' ', '.', '_')).rstrip()
        filename = os.path.join(safe_output_path, f"{sanitized_name}.strm")
        
        try:
            with open(filename, 'w') as f:
                f.write(item['url'])
        except IOError as e:
            logger.error(f"Could not write to file {filename}: {e}")


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
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching M3U file: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching M3U file: {e}")
    except ValueError as e:
        logger.error(f"Path validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")