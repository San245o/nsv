import os
import uuid
import subprocess
from contextlib import asynccontextmanager
from typing import Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request, Body, Response
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

# Configuration
TRIM_FOLDER = "trimmed_videos"
os.makedirs(TRIM_FOLDER, exist_ok=True)

# Video sources configuration
VIDEO_CONFIG = {
    "L2": {
        "video_file": "L2.mp4",
        "coordinates_file": "coordinates.csv",
        "gdrive_id": "1B-SySPfrSL2lietk3dKoZetIyfxJ-wfv"
    },
    "R2": {
        "video_file": "R2.mp4",
        "coordinates_file": "coordinates2.csv",
        "gdrive_id": "1cjWAkltEMEDP4x1hFm7gP0tVCw8l_Bi2"
    }
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Download videos if missing
    for config in VIDEO_CONFIG.values():
        if not os.path.exists(config["video_file"]):
            try:
                import gdown
                gdown.download(id=config["gdrive_id"], output=config["video_file"], quiet=True)
            except Exception as e:
                print(f"Failed to download video: {str(e)}")
    yield
    # Cleanup on shutdown could be added here

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Content-Length", "Content-Type"]
)

def get_timestamps(
    csv_path: str, 
    start_lat: float, 
    start_lon: float, 
    end_lat: float, 
    end_lon: float
) -> Optional[Tuple[float, float]]:
    """Find timestamps based on coordinates with memory efficiency"""
    try:
        # Use chunking for large CSV files
        df = pd.read_csv(csv_path, usecols=["lat", "lon", "timestamp_sec"])
        df.dropna(subset=["lat", "lon"], inplace=True)
        
        # Vectorized distance calculation
        df["distance_start"] = np.hypot(df["lat"] - start_lat, df["lon"] - start_lon)
        df["distance_end"] = np.hypot(df["lat"] - end_lat, df["lon"] - end_lon)
        
        start_idx = df["distance_start"].idxmin()
        end_idx = df["distance_end"].idxmin()
        
        start_ts = df.at[start_idx, "timestamp_sec"]
        end_ts = df.at[end_idx, "timestamp_sec"]
        
        if pd.isna(start_ts) or pd.isna(end_ts) or start_ts >= end_ts:
            return None
            
        return float(start_ts), float(end_ts)
    except Exception as e:
        print(f"Error processing timestamps: {str(e)}")
        return None

@app.post("/trim")
async def trim_video(data: Dict = Body(...), request: Request = None):
    """Trim video between coordinates with optimized FFmpeg settings"""
    try:
        source = data.get("source")
        if source not in VIDEO_CONFIG:
            raise HTTPException(status_code=400, detail="Invalid source video name")

        try:
            start_lat = float(data["start_lat"])
            start_lon = float(data["start_lon"])
            end_lat = float(data["end_lat"])
            end_lon = float(data["end_lon"])
        except (KeyError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid coordinate values")

        config = VIDEO_CONFIG[source]
        start_ts, end_ts = get_timestamps(
            config["coordinates_file"],
            start_lat, start_lon, end_lat, end_lon
        )
        
        if not start_ts or not end_ts:
            raise HTTPException(status_code=400, detail="Invalid coordinates or timestamps")

        output_filename = f"{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(TRIM_FOLDER, output_filename)

        # Optimized FFmpeg command for Linux/low memory
        cmd = [
            "ffmpeg",
            "-loglevel", "error",  # Reduce logging overhead
            "-y",  # Overwrite without asking
            "-ss", str(start_ts),
            "-i", config["video_file"],
            "-to", str(end_ts - start_ts),  # Use duration instead of end timestamp
            "-c:v", "libx264",
            "-preset", "ultrafast",  # Faster than 'fast'
            "-crf", "28",  # Slightly higher compression for smaller files
            "-movflags", "+faststart",
            "-f", "mp4",
            output_path
        ]

        try:
            # Use Popen with resource limits for memory safety
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=lambda: os.setpriority(os.PRIO_PROCESS, 0, 10)  # Lower priority
            ) as proc:
                stdout, stderr = proc.communicate(timeout=30)
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(proc.returncode, cmd, stderr)
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Video processing timed out")
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"FFmpeg error: {e.stderr.decode().strip()}")

        # Return URL with correct scheme
        base_url = str(request.base_url).replace("http://", "https://") if "cloudflare" in str(request.base_url) else str(request.base_url)
        return {"video_url": f"{base_url}video/{output_filename}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/video/{filename}")
async def serve_video(filename: str, request: Request):
    """Serve video with efficient streaming and range support"""
    file_path = os.path.join(TRIM_FOLDER, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Use FileResponse which handles range requests automatically
    return FileResponse(
        file_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(os.path.getsize(file_path)),
        }
    )

@app.get("/trimmed/count")
def count_trimmed_videos():
    """Count trimmed videos with efficient directory scanning"""
    try:
        count = sum(1 for f in os.listdir(TRIM_FOLDER) if f.endswith(".mp4"))
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting videos: {str(e)}")

@app.delete("/trimmed/delete-all")
def delete_all_trimmed_videos():
    """Delete all trimmed videos with error handling"""
    try:
        deleted = 0
        for f in os.listdir(TRIM_FOLDER):
            try:
                os.remove(os.path.join(TRIM_FOLDER, f))
                deleted += 1
            except:
                continue
        return {"deleted": deleted, "message": f"Deleted {deleted} videos"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting videos: {str(e)}")

#C:\Users\rishi>curl -X POST http://16.171.150.111:8000/trim -H "Content-Type: application/json" -d "{\"source\":\"R2\",\"start_lat\":26.35031,\"start_lon\":76.24826,\"end_lat\":26.3512,\"end_lon\":76.24843}"
{"video_url":"http://16.171.150.111:8000/video/06c4ea7c201847fbbb274e454aa17557.mp4"}
C:\Users\rishi>curl -X DELETE http://localhost:8000/trimmed/delete-all
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 501</p>
        <p>Message: Unsupported method ('DELETE').</p>
        <p>Error code explanation: HTTPStatus.NOT_IMPLEMENTED - Server does not support this operation.</p>
    </body>
</html>

C:\Users\rishi>curl -X DELETE http://16.171.150.111:8000/trimmed/delete-all
{"deleted":34,"message":"Deleted 34 videos"}
C:\Users\rishi>
