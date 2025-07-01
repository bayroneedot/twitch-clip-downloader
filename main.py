from fastapi import FastAPI, HTTPException
import requests
import re
import json
import logging

app = FastAPI()

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

        text = resp.text

        # Attempt to extract JSON data inside window.__INITIAL_STATE__ or similar
        json_data_match = re.search(r'window\.__INITIAL_STATE__\s?=\s?({.+?});</script>', text)
        if not json_data_match:
            raise HTTPException(status_code=500, detail="Could not find initial JSON state in clip page")

        json_data = json.loads(json_data_match.group(1))

        # Navigate the JSON data to find the clip video qualities
        try:
            clip = next(iter(json_data['clips'].values()))
            qualities = clip['videoQualities']
            if not qualities:
                raise Exception("No video qualities found")

            mp4_url = qualities[0]['source']  # usually highest quality first
            logging.info(f"Found mp4_url: {mp4_url}")

            return {"mp4_url": mp4_url}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting mp4 url: {str(e)}")

    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
