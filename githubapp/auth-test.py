import requests

client_id = "Iv1.8df72ad9560c774c"
header = {"Content-Type": "application/json", "Accept": "application/json"}
postdata = {"client_id": client_id}

# r = requests.post('https://github.com/login/device/code',data = postdata)
# print(r.text)

# device_code="44ca6ea747482bc5b338c383f4493da4a3d9632f"
device_code = "ca4cd2ac633bf6fadbe56363f8ce9e2f1e11e0fc"
payload = {
    "client_id": client_id,
    "device_code": device_code,
    "grant_type:": "urn:ietf:params:oauth:grant-type:device_code",
}
r = requests.post(
    "https://github.com/login/oauth/access_token", headers=header, json=payload
)
print(r.encoding)
print(r.status_code)
print(r.json())
