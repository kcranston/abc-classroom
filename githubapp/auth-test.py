import requests
import time
from ruamel.yaml import YAML

from argparse import ArgumentParser


def get_github_auth():
    """
    Attempts to open the local file '.abc-classroom.tokens.yml'
    containing github API authentication information. Returns the
    contents of the 'github' section. Returns an empty dictionary
    if the file does not exist.
    """
    yaml = YAML()
    try:
        with open(".abc-tokens.yml") as f:
            config = yaml.load(f)
        return config["github"]

    except FileNotFoundError:
        return {}


def write_github_auth(token_type, token_value):
    """
    Adds the (key,value) pair (token_type, token_value) to the github
    config file '.abc-tokens.yml', overwriting any existing
    value for the key. Creates the file if it does not exist.
    """
    yaml = YAML()
    currentvalues = get_github_auth()
    # print("current config values:")
    # for k,v in currentvalues.items():
    #     print("{} : {}".format(k,v))
    currentvalues[token_type] = token_value
    newconfig = {"github": currentvalues}
    # print("new config:")
    # for k,v in newconfig.items():
    #     print("{} : {}".format(k,v))
    with open(".abc-tokens.yml", "w") as f:
        yaml.dump(newconfig, f)


def get_login_code(client_id):
    # header = {"Content-Type": "application/json"}
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

    return device_code


def poll_for_status(client_id):
    # header = {"Content-Type": "application/json"}
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
    access_token_expiry = int(time.time()) + data["expires_in"]
    refresh_token_expiry = int(time.time()) + data["refresh_token_expires_in"]
    write_github_auth("access_token", data["access_token"])
    write_github_auth("access_token_expiry", access_token_expiry)
    write_github_auth("refresh_token", data["refresh_token"])
    write_github_auth("refresh_token_expiry", refresh_token_expiry)


def get_access_token():
    auth_info = get_github_auth()
    # check the expiry
    expiry = auth_info["access_token_expiry"]
    print("Access token expires at {}".format(time.ctime(expiry)))
    if expiry > time.time():
        access_token = auth_info["access_token"]
    else:
        print("access token expired; refreshing")
        access_token = None
    return access_token


def remote_repo_exists(org, repository):
    """Check if the remote repository exists for the organization."""
    access_token = get_access_token()
    if access_token is None:
        return
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "token {}".format(access_token),
    }
    r = requests.get(
        "https://api.github.com/repos/{}/{}".format(org, repository),
        headers=header,
    )
    status_code = r.status_code
    if status_code == 200:
        return True
    else:
        return False


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "client_id", help="""The client id of your github app."""
    )
    parser.add_argument(
        "--noauth",
        action="store_true",
        help="""Does not ask for device code; just poll API.""",
    )
    args = parser.parse_args()

    if not args.noauth:
        device_code = get_login_code(args.client_id)

        input("Press RETURN to continue after inputting the code successfully")

    poll_for_status(args.client_id)

    repo_name = "hub-ops"
    organization = "earthlab"

    if remote_repo_exists(organization, repo_name):
        print("repo {} exists!".format(repo_name))
    else:
        print("no repo {} :(".format(repo_name))
