import requests
import json

url = "http://localhost:8080/data"

data = {
    "device_id": "MCU_001",
    "temperature": 25.5,
    "humidity": 60.0,
    "analog_value": 512
}

try:
    response = requests.post(url, json=data)
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")