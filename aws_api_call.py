import requests
import json
from requests_aws4auth import AWS4Auth
import base64
import os
from dotenv import load_dotenv
import time
import threading

load_dotenv()

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_str

def predict_label(base64_string):
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_SERVICE = os.getenv("AWS_SERVICE") 
    AWS_REGION = os.getenv("AWS_REGION")

    api_url = "https://276weygzmg.execute-api.ap-south-1.amazonaws.com/prod/process_image"

    aws_auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_SERVICE)

    # image_path = "s.jpg" 
    # base64_string = image_to_base64(image_path)
    data = {
        "image": base64_string
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, json=data, headers=headers, auth=aws_auth)
    return response.json()

# def send_image(base64_string, user_id, scan_id, lat, lon, timestamp):
#     payload = {
#         "image": base64_string,
#         "latitude": str(lat),
#         "longitude": str(lon),
#         "timestamp": timestamp,
#         "mob_no": int(user_id),
#         "scan_id": scan_id  
#     }
#     print("User id and scan id", user_id, scan_id)
#     headers = {
#         "Content-Type": "application/json"
#     }
#     AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
#     AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
#     AWS_SERVICE = os.getenv("AWS_SERVICE") 
#     AWS_REGION = os.getenv("AWS_REGION")
    
#     API_URL = "https://276weygzmg.execute-api.ap-south-1.amazonaws.com/prod/process_image"
#     aws_auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_SERVICE)

#     # print("Sending image to AWS API...", flush=True)
#     response = requests.post(API_URL, json=payload, headers=headers, auth=aws_auth)
#     # print("Image sent successfully.", flush=True)
#     response_data = response.json()
#     print(json.loads(response_data["body"]).get("class"))
#     return json.loads(response_data["body"]).get("class")

def send_image(base64_string, user_id, scan_id, lat, lon, timestamp):
    payload = {
        "image": base64_string,
        "latitude": str(lat),
        "longitude": str(lon),
        "timestamp": timestamp,
        "mob_no": int(user_id),
        "scan_id": scan_id  
    }
    # print("User id and scan id", user_id, scan_id)
    headers = {
        "Content-Type": "application/json"
    }
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_SERVICE = os.getenv("AWS_SERVICE") 
    AWS_REGION = os.getenv("AWS_REGION")
    
    API_URL = "https://276weygzmg.execute-api.ap-south-1.amazonaws.com/prod/process_image"
    aws_auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_SERVICE)
    try:
        response = requests.post(API_URL, json=payload, headers=headers, auth=aws_auth)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)

        response_data = response.json()

        # Safely access "body" and "class"
        body = response_data.get("body")
        if not body:
            print("No 'body' found in response.")
            return None

        class_name = json.loads(body).get("class")
        print(class_name)
        return class_name

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None