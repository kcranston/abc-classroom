# Methods for generating user-to-server authentication tokens to perform
# actions on behalf of users
# Uses device flow authorization; see
# https://docs.github.com/en/free-pro-team@latest/developers/apps/
# identifying-and-authorizing-users-for-github-apps

import requests
from ruamel.yaml import YAML


def get_github_auth():
    """
    Attempts to open the local file '.abc-user-tokens.yml'
    containing github API authentication information. Returns the
    contents of the 'github' section. Returns an empty dictionary
    if the file does not exist.
    """
    yaml = YAML()
    try:
        with open(".abc-user-tokens.yml") as f:
            config = yaml.load(f)
        return config["github"]

    except FileNotFoundError:
        return {}


def write_github_auth(token_type, token_value):
    """
    Adds the (key,value) pair (token_type, token_value) to the github
    config file '.abc-user-tokens.yml', overwriting any existing
    value for the key. Creates the file if it does not exist.
    """
    yaml = YAML()
    currentvalues = get_github_auth()
    currentvalues[token_type] = token_value
    newconfig = {"github": currentvalues}
    with open(".abc-user-tokens.yml", "w") as f:
        yaml.dump(newconfig, f)


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
    write_github_auth("client_id", client_id)
    write_github_auth("device_code", device_code)

    # prompt the user to enter the code
    print(
        "To authorize this app, go to {} and enter the code {}".format(
            uri, user_code
        )
    )
    return r.status_code


def poll_for_status(client_id):
    githubconfig = get_github_auth()
    if githubconfig is None:
        print(
            """No github authentication info found; re-run without
            noauth flag to authenticate"""
        )
        return
    try:
        device_code = githubconfig["device_code"]
    except KeyError:
        print("No device code found; re-run without noauth flag to generate")
        return

    header = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "client_id": client_id,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    r = requests.post(
        "https://github.com/login/oauth/access_token",
        headers=header,
        json=payload,
    )
    print("Status code: ", r.status_code)
    print(r.json())
    data = r.json()
    write_github_auth("access_token", data["access_token"])


def get_access_token():
    auth_info = get_github_auth()
    try:
        access_token = auth_info["access_token"]
        return access_token
    except KeyError:
        print("No access token found")
        return None


def get_auth_header(token):
    header = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token),
    }
    return header
