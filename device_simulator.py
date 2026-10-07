import os
import math
import random
from datetime import datetime, timedelta

START_LAT = 12.9716
START_LON = 77.5946
TOTAL_DISTANCE_M = 5000
AVG_PACE_MIN_PER_KM = 5.5
BEARING_DEG = 45
SAMPLE_RATE_SEC = 1
STORAGE_DIR = "device_storage"

def move_point(lat, lon, bearing_deg, distance_m):
    bearing_rad = math.radians(bearing_deg)
    meters_per_deg_lat = 111320
    meters_per_deg_lon = 111320 * math.cos(math.radians(lat))
    d_lat = (distance_m * math.cos(bearing_rad)) / meters_per_deg_lat
    d_lon = (distance_m * math.sin(bearing_rad)) / meters_per_deg_lon
    return lat + d_lat, lon + d_lon

def simulate_run():
    avg_speed_mps = 1000 / (AVG_PACE_MIN_PER_KM * 60)
    total_duration_sec = int(TOTAL_DISTANCE_M / avg_speed_mps)
    halfway_sec = total_duration_sec // 2

    points = []
    lat, lon = START_LAT, START_LON
    start_time = datetime.utcnow()

    for t in range(0, total_duration_sec, SAMPLE_RATE_SEC):
        jitter = random.uniform(0.92, 1.08)
        step_distance = avg_speed_mps * SAMPLE_RATE_SEC * jitter
        bearing = BEARING_DEG if t < halfway_sec else (BEARING_DEG + 180) % 360
        lat, lon = move_point(lat, lon, bearing, step_distance)
        timestamp = start_time + timedelta(seconds=t)
        points.append((timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"), lat, lon))

    return points

def next_run_id():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    existing = [f for f in os.listdir(STORAGE_DIR) if f.startswith("RUN_")]
    numbers = []
    for f in existing:
        digits = f.replace("RUN_", "").split(".")[0]
        if digits.isdigit():
            numbers.append(int(digits))
    next_num = (max(numbers) + 1) if numbers else 1
    return f"RUN_{next_num:03d}"

def write_session_csv(points, run_id):
    filepath = os.path.join(STORAGE_DIR, f"{run_id}.csv")
    with open(filepath, "w") as f:
        f.write("timestamp,latitude,longitude\n")
        for timestamp, lat, lon in points:
            f.write(f"{timestamp},{lat:.6f},{lon:.6f}\n")
    return filepath

if __name__ == "__main__":
    run_id = next_run_id()
    points = simulate_run()
    filepath = write_session_csv(points, run_id)
    print(f"Device recorded session {run_id}: {len(points)} points")
    print(f"Saved to {filepath}")