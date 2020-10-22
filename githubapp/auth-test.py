import requests

from argparse import ArgumentParser


def get_login_code(client_id):

    header = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"client_id": client_id}
    link = "https://github.com/login/device/code"
    r = requests.post(link, headers=header, json=payload)
    print(r.json())
    data = r.json()
    device_code = data["device_code"]
    uri = data["verification_uri"]
    user_code = data["user_code"]

    # prompt the user to enter the code
    print(
        "To authorize this app, go to {} and enter the code {}".format(
            uri, user_code
        )
    )

    return device_code


def poll_for_status(client_id, device_code):
    header = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "client_id": client_id,
        "device_code": device_code,
        "grant_type:": "urn:ietf:params:oauth:grant-type:device_code",
    }
    r = requests.post(
        "https://github.com/login/oauth/access_token",
        headers=header,
        json=payload,
    )
    print(r.json())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "client_id", help="""The client id of your github app."""
    )
    args = parser.parse_args()

    # client_id = "Iv1.8df72ad9560c774c"
    print(args.client_id)
    device_code = get_login_code(args.client_id)

    input(
        "Press any key to continue once you have input the code successfully"
    )

    poll_for_status(args.client_id, device_code)
