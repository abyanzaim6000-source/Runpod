import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")

def upload_to_strava(gpx_filepath, run_id, access_token):
    url = "https://www.strava.com/api/v3/uploads"
    headers = {"Authorization": f"Bearer {access_token}"}
    with open(gpx_filepath, "rb") as f:
        files = {"file": f}
        data = {
            "name": f"RUNPOD {run_id}",
            "description": "Synced via RUNPOD receiver (Phase 3/4)",
            "data_type": "gpx",
        }
        response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "fake_run.gpx"
    result = upload_to_strava(gpx_filepath, run_id, access_token)   
    print("Upload response:")
    print(result)