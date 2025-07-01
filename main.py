import os
import asyncio
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from yt_dlp import YoutubeDL
from fastapi.responses import FileResponse

app = FastAPI()

TEMP_DIR = "/tmp"

def cleanup_file(path: str, delay_seconds: int = 300):
    async def _cleanup():
        await asyncio.sleep(delay_seconds)
        if os.path.exists(path):
            os.remove(path)
    return _cleanup()

@app.get("/download_clip")
async def download_clip(clip_url: str, background_tasks: BackgroundTasks):
    # Generate a unique filename per request
    file_id = str(uuid.uuid4())
    clip_path = os.path.join(TEMP_DIR, f"{file_id}.mp4")

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': clip_path,
        'quiet': True,
        'no_warnings': True,
    }

    # Download the clip (blocking, consider moving to threadpool if needed)
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([clip_url])
    except Exception as e:
        # Clean up partially downloaded file
        if os.path.exists(clip_path):
            os.remove(clip_path)
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

    # Schedule file deletion after 5 minutes (300 seconds)
    background_tasks.add_task(cleanup_file(clip_path))

    # Return the downloaded file (stream it)
    return FileResponse(clip_path, media_type="video/mp4", filename=f"clip-{file_id}.mp4")
