import serial
import time
import os

SERIAL_PORT = "/dev/cu.usbserial-5B070032381"  # update if yours differs
BAUD_RATE = 115200
STORAGE_DIR = "device_storage"

def send_command(ser, command, timeout=5):
    ser.write((command + "\n").encode())
    lines = []
    start = time.time()
    while time.time() - start < timeout:
        line = ser.readline().decode("ascii", errors="replace").strip()
        if not line:
            continue
        if line == "END" or line == "OK":
            lines.append(line)
            break
        if line.startswith("ERROR"):
            lines.append(line)
            break
        lines.append(line)
    return lines

def main():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)

    print("Waiting for device to boot...")
    start = time.time()
    ready = False
    while time.time() - start < 10:
        line = ser.readline().decode("ascii", errors="replace").strip()
        if line:
            print(f"  BOOT: {line}")
        if "ready" in line.lower():
            ready = True
            break

    if not ready:
        print("WARNING: never saw the device's ready message. Proceeding anyway.")

    time.sleep(0.5)

    print("Requesting file list from device...")
    response = send_command(ser, "LIST")
    print(f"  Raw response: {response}")  # debug - remove later
    filenames = [line for line in response if line != "END" and not line.startswith("ERROR")]

    if not filenames:
        print("No unsynced sessions on device.")
        ser.close()
        return

    print(f"Found {len(filenames)} unsynced session(s) on device: {filenames}")

    for filename in filenames:
        print(f"\nDownloading {filename}...")
        response = send_command(ser, f"DUMP {filename}", timeout=15)

        if not response or not response[0].startswith("BEGIN"):
            print(f"  ERROR: unexpected response for {filename}")
            continue

        csv_lines = response[1:-1]
        local_path = os.path.join(STORAGE_DIR, filename)
        with open(local_path, "w") as f:
            f.write("\n".join(csv_lines) + "\n")

        print(f"  Saved {len(csv_lines) - 1} data rows to {local_path}")

        print(f"  Acknowledging {filename}...")
        ack_response = send_command(ser, f"ACK {filename}")
        if "OK" in ack_response:
            print(f"  Device marked {filename} as synced.")
        else:
            print(f"  WARNING: device did not confirm sync for {filename}")

    ser.close()
    print("\nDone. Run receiver.py next to convert and upload.")


if __name__ == "__main__":
    main()