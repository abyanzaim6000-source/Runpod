import serial
import os
from datetime import datetime, timezone

STORAGE_DIR = "device_storage"
SERIAL_PORT = "/dev/cu.usbserial-5B070032381"  # update if yours differs
BAUD_RATE = 115200

def nmea_to_decimal(raw_value, direction):
    if not raw_value:
        return None
    value = float(raw_value)
    degrees = int(value / 100)
    minutes = value - (degrees * 100)
    decimal = degrees + minutes / 60
    if direction in ("S", "W"):
        decimal = -decimal
    return decimal

def parse_gga(sentence):
    fields = sentence.split(",")
    if len(fields) < 10:
        return None

    time_str = fields[1]
    lat_raw, lat_dir = fields[2], fields[3]
    lon_raw, lon_dir = fields[4], fields[5]
    fix_quality = fields[6]

    if fix_quality == "0" or not lat_raw or not lon_raw or not time_str:
        return None

    lat = nmea_to_decimal(lat_raw, lat_dir)
    lon = nmea_to_decimal(lon_raw, lon_dir)

    hh, mm, ss = int(time_str[0:2]), int(time_str[2:4]), int(time_str[4:6])
    now = datetime.now(timezone.utc)
    timestamp = now.replace(hour=hh, minute=mm, second=ss, microsecond=0)

    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"), lat, lon

def next_run_id():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    existing = [f for f in os.listdir(STORAGE_DIR) if f.startswith("RUN_")]
    numbers = [int(f.replace("RUN_", "").split(".")[0])
               for f in existing if f.replace("RUN_", "").split(".")[0].isdigit()]
    return f"RUN_{(max(numbers) + 1) if numbers else 1:03d}"

def main():
    run_id = next_run_id()
    filepath = os.path.join(STORAGE_DIR, f"{run_id}.csv")

    print(f"Logging live GPS data to {filepath}")
    print("Walk around now. Press Ctrl+C to stop and save.")

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    point_count = 0

    with open(filepath, "w") as f:
        f.write("timestamp,latitude,longitude\n")
        try:
            while True:
                line = ser.readline().decode("ascii", errors="replace").strip()
                if line:
                    print(f"RAW: {line}")  # debug - remove later
                if line.startswith("$GNGGA") or line.startswith("$GPGGA"):
                    result = parse_gga(line)
                    if result:
                        timestamp, lat, lon = result
                        f.write(f"{timestamp},{lat:.6f},{lon:.6f}\n")
                        f.flush()
                        point_count += 1
                        print(f"  Point {point_count}: {timestamp} lat={lat:.6f} lon={lon:.6f}")
        except KeyboardInterrupt:
            print(f"\nStopped. Recorded {point_count} points to {filepath}")

if __name__ == "__main__":
    main()