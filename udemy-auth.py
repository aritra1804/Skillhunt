import base64
import requests

# CLIENT_ID = 'JfHN7pmHzxTDZ4RGe9bqcpqwhxPVmwdLFX2npJ9S'
# CLIENT_SECRET = 'gCYnV43f2jsbkrCDyNywUPOk20bKFnIZcKAp0sSN3rtBgR9HjvY5IC69vETJIY4sWFNGmbJHTdWgYxZUsybKxrbcu6G1T67n9QD3Do1jRle2WE9dM3UCx1RVLCVGihlQ'

# # Encode credentials for Basic Auth
# credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
# encoded_credentials = base64.b64encode(credentials.encode()).decode()

# headers = {
#     "Authorization": f"Basic {encoded_credentials}",
#     "Accept": "application/json"
# }

# response = requests.get("https://www.udemy.com/api-2.0/courses/", headers=headers)
# print(response.status_code, response.text)



response = requests.get("https://api.github.com")
print(response.status_code)
print(response.json())

