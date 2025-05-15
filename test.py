import requests
import base64

# 1. Convert your image to base64
image_path = "/home/thahseer/Downloads/aseancountrieschinadrivinglicens/Cambodia license 1.jpg"
with open(image_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

# 2. Prepare payload
payload = {
    "recordId": "",
    "image": f"data:image/png;base64,{base64_image}"
}

# 3. Set headers
headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "key": "sjvRQ32WV0bvaWq26mu2hw9no"  # Replace with your actual API key if different
}

# 4. API endpoint
url = "https://api-uat.pixl.ai/driving-licence-data-extraction-uat/driving-license/1.0"

# 5. Make POST request
response = requests.post(url, json=payload, headers=headers)

# 6. Print the response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
