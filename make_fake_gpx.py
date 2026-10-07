from datetime import datetime, timedelta

# A tiny fake route: 5 points, roughly walking/jogging pace
# (lat, lon) pairs - these are just made-up points close together
fake_points = [
    (12.9716, 77.5946),
    (12.9720, 77.5950),
    (12.9724, 77.5954),
    (12.9728, 77.5958),
    (12.9732, 77.5962),
]

start_time = datetime.utcnow()

def build_gpx(points, start_time, seconds_between_points=30):
    gpx_header = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="RUNPOD" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>RUNPOD Fake Run</name>
    <trkseg>
'''
    gpx_footer = '''    </trkseg>
  </trk>
</gpx>
'''

    body = ""
    for i, (lat, lon) in enumerate(points):
        point_time = start_time + timedelta(seconds=i * seconds_between_points)
        timestamp_str = point_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        body += f'      <trkpt lat="{lat}" lon="{lon}">\n'
        body += f'        <time>{timestamp_str}</time>\n'
        body += f'      </trkpt>\n'

    return gpx_header + body + gpx_footer

gpx_content = build_gpx(fake_points, start_time)

with open("fake_run.gpx", "w") as f:
    f.write(gpx_content)

print("fake_run.gpx created successfully.")