import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Define the Shutterstock API token
SHUTTERSTOCK_API_TOKEN = os.getenv('TOKEN')

# Create headers for authorization
headers = {
    'Authorization': f'Bearer {SHUTTERSTOCK_API_TOKEN}',
    'Accept': 'application/json'
}

# Function to read JSON data from a file
def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

# Function to check if an image is already downloaded
def is_image_downloaded(image_id):
    return os.path.exists(f'./images/{image_id}.jpg')

# Function to download an image
def download_image(license_id, image_id):
    download_endpoint = f'https://api.shutterstock.com/v2/images/licenses/{license_id}/downloads'
    response = requests.post(download_endpoint, headers=headers)
    
    if response.status_code == 200:
        download_url = response.json()['url']
        image_response = requests.get(download_url)
        if image_response.status_code == 200:
            with open(f'./images/{image_id}.jpg', 'wb') as img_file:
                img_file.write(image_response.content)
            print(f"Downloaded image {image_id}")
        else:
            print(f"Failed to download image {image_id}")
    else:
        print("Response gives status code: ", response.status_code)
        print(f"Failed to get download URL for license {license_id}")

# Function to process and download images with rate limiting
def process_images(image_data):
    images_downloaded = 0
    start_time = datetime.now()

    for image in image_data:
        license_id = image['id']
        image_id = image['image']['id']
        
        if not is_image_downloaded(image_id):
            download_image(license_id, image_id)
            images_downloaded += 1

            # Respect rate limits: 5 images per minute, 100 images per hour
            if images_downloaded % 5 == 0:
                elapsed_time = (datetime.now() - start_time).total_seconds()
                if elapsed_time < 60:
                    time_to_wait = 60 - elapsed_time
                    print(f"Waiting for {time_to_wait} seconds to respect rate limits")
                    time.sleep(time_to_wait)
                start_time = datetime.now()
            
            if images_downloaded % 100 == 0:
                elapsed_time = (datetime.now() - start_time).total_seconds()
                if elapsed_time < 3600:
                    time_to_wait = 3600 - elapsed_time
                    print(f"Waiting for {time_to_wait} seconds to respect rate limits")
                    time.sleep(time_to_wait)
                start_time = datetime.now()
            time.sleep(10)

# Ensure the images directory exists
if not os.path.exists('./images'):
    os.makedirs('./images')

# Read image data from JSON files
data_part_1 = read_json_file('licensed_images_data_part_1.json')
data_part_2 = read_json_file('licensed_images_data_part_2.json')

# Combine data from both parts
all_image_data = data_part_1 + data_part_2

# Process and download images
process_images(all_image_data)
