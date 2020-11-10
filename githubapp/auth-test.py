# Testing user-to-server authentication tokens. Used to perform
# actions on behalf of users
# See https://docs.github.com/en/free-pro-team@latest/developers/apps/
# identifying-and-authorizing-users-for-github-apps

import requests
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
    write_github_auth("access_token", data["access_token"])


def get_access_token():
    auth_info = get_github_auth()
    try:
        access_token = auth_info["access_token"]
        return access_token
    except KeyError:
        print("No access token found")
        return None


def remote_repo_exists(org, repository, token):
    """Check if the remote repository exists for the organization."""
    header = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token),
    }
    r = requests.get(
        "https://api.github.com/repos/{}/{}".format(org, repository),
        headers=header,
    )
    status_code = r.status_code
    # print(r.json())
    if status_code == 200:
        return True
    else:
        return False


def get_auth_header(token):
    header = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token),
    }
    return header


def update_issue(token):
    print("Trying to update issue")
    # header = {
    #     "Content-Type": "application/json",
    #     "Accept": "application/vnd.github.v3+json",
    #     "Authorization": "token {}".format(token),
    # }
    payload = {
        "title": "Create default commit message for abc-update-template"
    }
    r = requests.patch(
        "https://api.github.com/repos/earthlab/abc-classroom/issues/310",
        headers=get_auth_header(token),
        json=payload,
    )
    print(r.status_code)
    print(r.json())


def get_user_installations(token):
    # GET /user/installations
    r = requests.get(
        "https://api.github.com/user/installations",
        headers=get_auth_header(token),
    )
    print(r.status_code)
    print(r.json())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "client_id", help="""The client id of your github app."""
    )

    args = parser.parse_args()

    # There are three steps:
    # Check for presence of authorization info in the file .abc-tokens.yaml
    # If the file does not exist, start by getting a login code for the user
    # If authorization info exists, check that the access_token is present
    # If it is not present, poll for an access code using the device code
    # If we have a valid access_token, then call the API using that token

    auth_info = get_github_auth()
    if not auth_info:
        get_login_code(args.client_id)
        input("Press RETURN to continue after inputting the code successfully")
        poll_for_status(args.client_id)

    token = get_access_token()
    if token is None:
        poll_for_status(args.client_id)

    get_user_installations(token)

    print("Get public repo")
    repo_name = "hub-ops"
    organization = "earthlab"

    if remote_repo_exists(organization, repo_name, token):
        print(" repo {} exists!".format(repo_name))
    else:
        print(" no repo {} :(".format(repo_name))

    print("Get private repo")
    repo_name = "spring-2020-eapython-nbgrader"
    organization = "earth-analytics-edu"

    if remote_repo_exists(organization, repo_name, token):
        print(" repo {} exists!".format(repo_name))
    else:
        print(" no repo {} :(".format(repo_name))

    update_issue(token)
