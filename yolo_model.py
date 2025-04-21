import cv2
import numpy as np
import base64
import time
import asyncio
from ultralytics import YOLO
from aws_api_call import send_image
import threading
import os

def numpy_to_base64(image_np):
    _, buffer = cv2.imencode('.jpg', image_np)
    return base64.b64encode(buffer).decode('utf-8')

def detect_and_crop_leaves(image_path, model_path='yolo11x_leaf.pt'):
    model = YOLO(model_path)
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Could not read image.")
        return []
    
    results = model(image)
    base64_leaves = []
    
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            cropped_leaf = image[y1:y2, x1:x2]
            base64_leaf = numpy_to_base64(cropped_leaf)
            base64_leaves.append(base64_leaf)
    
    return base64_leaves

# image_path = '1.jpg'
# start = time.perf_counter()
# base64_images = detect_and_crop_leaves(image_path)
# print(f'Found {len(base64_images)} leaves.')
# results = []

# for base64_string in base64_images:
#     results.append(predict_label(base64_string))

# end = time.perf_counter()

# print(f"Process took {end - start:.3f} seconds")

# print(results)

async def process_leaves(image_path, user_id, scan_id, lat, lon, timestamp):
    base64_images = detect_and_crop_leaves(image_path)  
    print(f'Found {len(base64_images)} leaves in {image_path}.')
    # tasks = [asyncio.to_thread(send_image, img) for img in base64_images]
    # await asyncio.gather(*tasks)
    async def thread_task(img):
        await asyncio.to_thread(send_image, img, user_id, scan_id, lat, lon, timestamp)

    tasks = [thread_task(img) for img in base64_images]
    await asyncio.gather(*tasks)

def call_api_in_background(image_path, user_id, scan_id, lat, lon, timestamp):
    def run_in_background(image_path, user_id, scan_id, lat, lon, timestamp):
        asyncio.run(process_leaves(image_path, user_id, scan_id, lat, lon, timestamp))

    thread = threading.Thread(
        target=run_in_background,
        args=(image_path, user_id, scan_id, lat, lon, timestamp),
        daemon=True
    )
    thread.start()
    return thread

# image_path= ["drone_images/1.jpg", "drone_images/2.jpg"] 
# image_folder = "drone_images"
# image_path = []

# for filename in os.listdir(image_folder):
#     if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
#         image = os.path.join(image_folder, filename)
#         image_path.append(image)

# threads = []
# results = []

# for image in image_path:
#     # print("Processing image:", image)
#     result_list = []  # Separate result list per image
#     thread = call_api_in_background(image, result_list)
#     thread.join()  # ⏳ Wait for processing of this image to finish
#     results.append((image, result_list))
#     # threads.append(thread)
#     # time.sleep(2)

# # Optional: wait for all threads to finish
# # for thread in threads:
# #     thread.join()

# # Print results
# for image, result_list in results:
#     print(f"📸 Results for {image}:")
#     for res in result_list:
#         print(res)

# thread = call_api_in_background("drone_images/5.jpg", results)

# def run_in_background(image_path, results):
#     asyncio.run(process_leaves(image_path, results))

# thread = threading.Thread(target=run_in_background, args=(image_path, results), daemon=True)
# thread.start()

# time.sleep(1)
# thread.join()
# for res in results:
#     print(res)

# Main thread continues to run
# for _ in range(10):
#     # print("Hello world")
#     time.sleep(1)

