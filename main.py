from fastapi import FastAPI, HTTPException
from yt_dlp import YoutubeDL

app = FastAPI()

@app.get("/get_mp4")
def get_mp4(clip_url: str):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(clip_url, download=False)
            video_url = info.get('url')
            if not video_url:
                raise HTTPException(status_code=404, detail="No video URL found")
            return {"mp4_url": video_url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting clip: {str(e)}")
