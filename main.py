from fastapi import FastAPI, HTTPException
import requests
import re
import json
import logging

app = FastAPI()

# Setup basic logging
logging.basicConfig(level=logging.INFO)

@app.get("/get_mp4")
def get_mp4(clip_url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        logging.info(f"Fetching clip page: {clip_url}")
        resp = requests.get(clip_url, headers=headers)
        logging.info(f"Response status: {resp.status_code}")

        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Clip not found (status {resp.status_code})")

        logging.info(f"Page content length: {len(resp.text)}")

        match = re.search(r'"quality_options":(\[.*?\])', resp.text)
        if not match:
            raise HTTPException(status_code=500, detail="Could not parse clip info (pattern not found)")

        quality_options = json.loads(match.group(1))
        logging.info(f"Found {len(quality_options)} quality options")

        if not quality_options:
            raise HTTPException(status_code=500, detail="No quality options found in clip info")

        mp4_url = quality_options[0]['source']
        logging.info(f"Returning mp4_url: {mp4_url}")

        return {"mp4_url": mp4_url}

    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
