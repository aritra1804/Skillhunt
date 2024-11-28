import requests
import base64
import time
import pandas as pd

response = requests.get(BASE_URL, headers=headers, params=params)
if response.status_code == 200:
    data = response.json()
    courses = data.get("results", [])
    print(courses[0])  # Print the first course to inspect available fields
