import os
import time
import requests
import sys

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")

def check_status(upload_id):
    url = f"https://www.strava.com/api/v3/uploads/{upload_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    UPLOAD_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 21056261660

    for attempt in range(15):
        result = check_status(UPLOAD_ID)
        print(f"Attempt {attempt + 1}: {result}")

        if result.get("error"):
            print("Upload failed with an error.")
            break

        if result.get("activity_id"):
            print(f"SUCCESS! Activity created with ID: {result['activity_id']}")
            print(f"View it at: https://www.strava.com/activities/{result['activity_id']}")
            break

        print("Still processing, waiting 2 seconds...")
        time.sleep(2)
    else:
        print("Gave up after 10 attempts — check manually on Strava.")