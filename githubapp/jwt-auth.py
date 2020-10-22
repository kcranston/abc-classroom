import jwt
import time
import requests


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


if __name__ == "__main__":

    pem_file = "/Users/karen/.ssh/abcclassroomtest.2020-10-07.private-key.pem"

    with open(pem_file, "r") as rsa_priv_file:
        private_key = rsa_priv_file.read()

    print(time.gmtime())
    payload = {
        "iat": time.time(),
        "exp": time.time() + (7 * 60),
        "iss": "83862",
    }

    print(time.ctime(payload["iat"]))
    print(time.ctime(payload["exp"]))
    encodedkey = jwt.encode(payload, private_key, algorithm="RS256")

    header = {"Accept": "application/vnd.github.v3+json"}

    r = requests.get(
        "https://api.github.com/app",
        headers=header,
        auth=BearerAuth(encodedkey.decode()),
    )
    print(r.status_code)
    print(r.text)
    # print(r.headers)
