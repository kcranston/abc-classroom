import requests

client_id = "Iv1.8df72ad9560c774c"
header = {"Content-Type": "application/json", "Accept": "application/json"}

# Step 1
payload1 = {"client_id": client_id}
r = requests.post(
    "https://github.com/login/device/code", headers=header, json=payload1
)
data = r.json()
device_code = data["device_code"]
uri = data["verification_uri"]
user_code = data["user_code"]

# Step 2
print(
    "To authorize this app, go to {} and enter the code {}".format(
        uri, user_code
    )
)
input("Press any key to continue once you have input the code successfully")

# Step 3
payload3 = {
    "client_id": client_id,
    "device_code": device_code,
    "grant_type:": "urn:ietf:params:oauth:grant-type:device_code",
}
r = requests.post(
    "https://github.com/login/oauth/access_token",
    headers=header,
    json=payload3,
)
print(r.json())
