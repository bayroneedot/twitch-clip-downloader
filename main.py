from fastapi import FastAPI, HTTPException
import requests
import re
import json

app = FastAPI()

@app.get("/get_mp4")
def get_mp4(clip_url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(clip_url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Clip not found")

        match = re.search(r'"quality_options":(\[.*?\])', resp.text)
        if not match:
            raise HTTPException(status_code=500, detail="Could not parse clip info")

        quality_options = json.loads(match.group(1))
        mp4_url = quality_options[0]['source']
        return {"mp4_url": mp4_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
