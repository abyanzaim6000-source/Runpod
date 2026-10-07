import os
import glob
import csv
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
STORAGE_DIR = "device_storage"

def refresh_access_token():
    url = "https://www.strava.com/oauth/token"
    response = requests.post(url, data={
        "client_id": os.getenv("STRAVA_CLIENT_ID"),
        "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN"),
    })
    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"]

def find_unsynced_sessions():
    pattern = os.path.join(STORAGE_DIR, "RUN_*.csv")
    all_files = glob.glob(pattern)
    return [f for f in all_files if ".synced." not in f]

def read_session_csv(filepath):
    points = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            points.append(row)
    return points

def validate_session(points):
    if len(points) < 2:
        return False, "Session has fewer than 2 points"
    timestamps = [datetime.strptime(p["timestamp"], "%Y-%m-%dT%H:%M:%SZ") for p in points]
    if timestamps != sorted(timestamps):
        return False, "Timestamps are not in order"
    return True, "OK"

def convert_to_gpx(points, run_id):
    gpx_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="RUNPOD" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>RUNPOD {run_id}</name>
    <trkseg>
'''
    gpx_footer = '''    </trkseg>
  </trk>
</gpx>
'''
    body = ""
    for p in points:
        body += f'      <trkpt lat="{p["latitude"]}" lon="{p["longitude"]}">\n'
        body += f'        <time>{p["timestamp"]}</time>\n'
        body += f'      </trkpt>\n'

    gpx_content = gpx_header + body + gpx_footer
    gpx_filepath = os.path.join(STORAGE_DIR, f"{run_id}.gpx")
    with open(gpx_filepath, "w") as f:
        f.write(gpx_content)
    return gpx_filepath

def upload_to_strava(gpx_filepath, run_id, access_token):
    url = "https://www.strava.com/api/v3/uploads"
    headers = {"Authorization": f"Bearer {access_token}"}
    with open(gpx_filepath, "rb") as f:
        files = {"file": f}
        data = {
            "name": f"RUNPOD {run_id}",
            "description": "Synced via RUNPOD receiver (Phase 4)",
            "data_type": "gpx",
        }
        response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()
    return response.json()

def mark_synced(csv_filepath, run_id):
    new_path = os.path.join(STORAGE_DIR, f"{run_id}.synced.csv")
    os.rename(csv_filepath, new_path)
    return new_path

def process_session(csv_filepath, access_token):
    run_id = os.path.basename(csv_filepath).replace(".csv", "")
    print(f"\nProcessing {run_id}...")

    points = read_session_csv(csv_filepath)
    valid, message = validate_session(points)
    if not valid:
        print(f"  VALIDATION FAILED: {message}")
        return

    print(f"  Validated: {len(points)} points, OK")

    gpx_filepath = convert_to_gpx(points, run_id)
    print(f"  Converted to GPX: {gpx_filepath}")

    result = upload_to_strava(gpx_filepath, run_id, access_token)
    print(f"  Uploaded. Response: {result}")

    mark_synced(csv_filepath, run_id)
    print(f"  Marked as synced.")

if __name__ == "__main__":
    sessions = find_unsynced_sessions()
    if not sessions:
        print("No unsynced sessions found.")
    else:
        print("Refreshing Strava access token...")
        access_token = refresh_access_token()
        print("Token refreshed.")

        print(f"Found {len(sessions)} unsynced session(s): {sessions}")
        for session in sessions:
            process_session(session, access_token)