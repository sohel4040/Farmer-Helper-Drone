import threading
import time
import json
import random
import paho.mqtt.client as mqtt
import os
from yolo_model import call_api_in_background
from datetime import datetime, timezone
import requests

# Globals
scan_thread = None
stop_event = threading.Event()
current_scan_id = None

BROKER = "a1zg5uoiko253q-ats.iot.ap-south-1.amazonaws.com"
TOPIC = "drone/control"

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data["loc"] 
        latitude, longitude = loc.split(",")
        return float(latitude), float(longitude)
    except Exception as e:
        print("Error:", e)
        return None, None


def start_scan_process(scan_id,  mob_no):
    print(f"Starting scan process for Scan ID: {scan_id}")
    image_folder = "drone_images"
    image_files = sorted([
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    counter = 0
    while not stop_event.is_set():
        if image_files and counter != 5:
            image_path = image_files[counter % len(image_files)]
            lat, lon = get_location()
            print(f"📸 Captured image: {image_path}")
            timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            call_api_in_background(image_path, mob_no, scan_id, lat, lon, timestamp)
            counter += 1
        else:
            print("⚠️ No images in folder.")
        time.sleep(10)
    # while not stop_event.is_set():
        # fake_image_id = random.randint(1000, 9999)
        # print(f"📸 Captured image: image_{fake_image_id}.jpg")
        
        # # To be done
        # captured_image = capture_image_from_drone()

        # run_in_background(captured_image, scan_id)

        # time.sleep(2)
    print(f"🛑 Scan process stopped Scan ID: {scan_id}")

def on_message(client, userdata, msg):
    global scan_thread, stop_event, current_scan_id

    try:
        payload = json.loads(msg.payload.decode())
        action = payload.get("action")
        scan_id = payload.get("scan_id")
        mob_no = payload.get("mob_no")
        print(payload)
        if action == "start":
            if scan_thread is None or not scan_thread.is_alive():
                stop_event.clear()
                current_scan_id = scan_id
                scan_thread = threading.Thread(target=start_scan_process, args=(scan_id, mob_no), daemon=True)
                scan_thread.start()
            else:
                print("⚠️ Scan already running.")

        elif action == "stop":
            if scan_thread and scan_thread.is_alive():
                stop_event.set()
                scan_thread.join(timeout=3)
                print("✅ Scan process stopped.")
            else:
                print("⚠️ No scan to stop.")
            current_scan_id = None

    except Exception as e:
        print(f"❌ Error in on_message: {e}")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to broker.")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Connection failed. Code: {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set("AmazonRootCA1.pem", certfile="a68c644cfece7899130d0d2af04f3e895d173c9da70d7782cde41434e6b6feea-certificate.pem.crt", keyfile="a68c644cfece7899130d0d2af04f3e895d173c9da70d7782cde41434e6b6feea-private.pem.key")
client.connect(BROKER, 8883, 60)
print("Connected")
client.loop_start()

try:
    print("💡 Waiting for MQTT messages...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("👋 Exiting...")
    stop_event.set()
    if scan_thread and scan_thread.is_alive():
        scan_thread.join()
    client.loop_stop()
    client.disconnect()
