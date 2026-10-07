RUNPOD is a standalone wearable running tracker built from the ground up — no phone, no smartwatch needed during the run.

The device (ESP32 + GPS/GNSS module + IMU) records a complete run independently: GPS handles route, distance, and pace, while the IMU handles motion detection, step cadence, and run/walk classification. After the run, data syncs to a companion app over Bluetooth Low Energy, which processes it into an activity file and uploads it to the user's Strava account. The goal isn't to build another fitness social network — it's to prove that real hardware can replace carrying a phone, while still landing cleanly in the tools runners already use.

The project is being built in deliberate phases rather than all at once:

Software-first validation — proved the full Strava OAuth → GPX → upload pipeline using simulated data, before any hardware was involved
Simulated device architecture — a device/receiver split (file-based handoff, batch sync, validation) mirroring the real system's eventual shape
Real GPS hardware — NEO-6M module wired to an ESP32, parsing live NMEA sentences, uploading real GPS-recorded routes to Strava
On-device storage — sessions recorded to flash (LittleFS), surviving power loss, retrievable after the device is disconnected and reconnected
(in progress) IMU integration, BLE sync protocol, and a mobile companion app

Each phase is proven independently before the next begins — GPS, storage, motion sensing, and wireless sync are each validated in isolation first, so failures are easy to isolate and nothing gets built on unverified assumptions.

Tech: ESP32 (PlatformIO/Arduino), NEO-6M GPS, MPU-6050 IMU, Python (prototyping/testing tools), Strava API/OAuth, GPX.
