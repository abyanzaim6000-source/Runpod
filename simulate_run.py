import math
import random
from datetime import datetime, timedelta

# ---- Run parameters ----
START_LAT = 12.9716
START_LON = 77.5946
TOTAL_DISTANCE_M = 5000       # 5 km total (2.5 km out, 2.5 km back)
AVG_PACE_MIN_PER_KM = 5.5     # 5:30 min/km average pace
BEARING_DEG = 45              # outbound direction (NE); return = +180
SAMPLE_RATE_SEC = 1           # 1 GPS point per second

EARTH_RADIUS_M = 6371000

def move_point(lat, lon, bearing_deg, distance_m):
    """Move a lat/lon point a given distance (m) along a bearing (deg)."""
    bearing_rad = math.radians(bearing_deg)
    # Approximate meters-per-degree at this latitude
    meters_per_deg_lat = 111320
    meters_per_deg_lon = 111320 * math.cos(math.radians(lat))

    d_lat = (distance_m * math.cos(bearing_rad)) / meters_per_deg_lat
    d_lon = (distance_m * math.sin(bearing_rad)) / meters_per_deg_lon

    return lat + d_lat, lon + d_lon

def simulate_run():
    avg_speed_mps = 1000 / (AVG_PACE_MIN_PER_KM * 60)  # meters per second
    total_duration_sec = int(TOTAL_DISTANCE_M / avg_speed_mps)
    halfway_sec = total_duration_sec // 2

    points = []
    lat, lon = START_LAT, START_LON
    distance_covered = 0.0
    start_time = datetime.utcnow()

    for t in range(0, total_duration_sec, SAMPLE_RATE_SEC):
        # Add small realistic pace jitter (+/- 8%)
        jitter = random.uniform(0.92, 1.08)
        step_distance = avg_speed_mps * SAMPLE_RATE_SEC * jitter

        bearing = BEARING_DEG if t < halfway_sec else (BEARING_DEG + 180) % 360
        lat, lon = move_point(lat, lon, bearing, step_distance)
        distance_covered += step_distance

        timestamp = start_time + timedelta(seconds=t)
        points.append({
            "lat": lat,
            "lon": lon,
            "time": timestamp,
        })

    return points

def build_gpx(points):
    gpx_header = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="RUNPOD" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>RUNPOD Simulated Run</name>
    <trkseg>
'''
    gpx_footer = '''    </trkseg>
  </trk>
</gpx>
'''
    body = ""
    for p in points:
        timestamp_str = p["time"].strftime("%Y-%m-%dT%H:%M:%SZ")
        body += f'      <trkpt lat="{p["lat"]:.6f}" lon="{p["lon"]:.6f}">\n'
        body += f'        <time>{timestamp_str}</time>\n'
        body += f'      </trkpt>\n'
    return gpx_header + body + gpx_footer

if __name__ == "__main__":
    points = simulate_run()
    gpx_content = build_gpx(points)

    with open("simulated_run.gpx", "w") as f:
        f.write(gpx_content)

    duration_min = len(points) * SAMPLE_RATE_SEC / 60
    print(f"Simulated run created: {len(points)} points, ~{duration_min:.1f} minutes")
    print("Saved to simulated_run.gpx")