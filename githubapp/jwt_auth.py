# Testing installation access tokens, used to perform actions on
# behalf of the GitHub App
# See https://docs.github.com/en/free-pro-team@latest/developers/
# apps/authenticating-with-github-apps

import jwt
import time
import requests
import json
from ruamel.yaml import YAML
from argparse import ArgumentParser


def generate_jwt():
    """Generates a JSON Web Token (JWT), given the app id. Has a
    short (<10min) expiry, so we use it right away and don't store it. """

    pem_file = "/Users/karen/.ssh/abcclassroomtest.2020-10-07.private-key.pem"
    app_id = "83862"

    with open(pem_file, "r") as rsa_priv_file:
        private_key = rsa_priv_file.read()

    issued = int(time.time())
    expiry = int(time.time()) + (8 * 60)
    payload = {"iat": issued, "exp": expiry, "iss": app_id}

    print("JWT generated; expires at {}".format(time.ctime(expiry)))
    encodedkey = jwt.encode(payload, private_key, algorithm="RS256")
    return encodedkey


def read_token():
    yaml = YAML()
    try:
        with open(".abc-access-token.yml") as f:
            config = yaml.load(f)
        return config["access_token"]

    except FileNotFoundError:
        return {}
    except KeyError:
        return {}


def get_installations(printlist=False):
    """Getting app installations only requires a JWT, not an access key.
    See https://docs.github.com/en/free-pro-team@latest/rest/reference/
    apps#list-installations-for-the-authenticated-app."""
    encodedkey = generate_jwt()
    header = _get_jwt_header(encodedkey)
    r = requests.get(
        "https://api.github.com/app/installations", headers=header
    )
    installation_list = r.json()
    if printlist:
        print(json.dumps(installation_list, sort_keys=True, indent=4))
    return installation_list


def _get_access_token_header(token):
    """Generate and return the header used for authenticating using an
    access token."""
    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token),
    }
    return header


def _get_jwt_header(encodedkey):
    """Generate and return the header used for authenticating using a JWT"""
    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer {}".format(encodedkey.decode()),
    }
    return header


def remote_repo_exists(org, repository, token):
    """Check if the remote repository exists for the organization."""
    header = {
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


def get_repos(token):
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


def update_issue(token):
    print("Trying to update issue")
    header = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token),
    }
    payload = {"title": "add zshrc function for creating conda envs"}
    r = requests.patch(
        "https://api.github.com/repos/kcranston/my_configs/issues/1",
        headers=header,
        json=payload,
    )
    print(r.status_code)
    print(r.json())


def _generate_new_token(installation_id):
    # if there is no current access_token, or if it is expired, we generate
    # a new one by first
    # generating a JWT token and then exchanging that for an access token
    encodedkey = generate_jwt()

    # Exchange the JWT for an installation access token
    url = "https://api.github.com/app/installations/{}/access_tokens".format(
        installation_id
    )
    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer {}".format(encodedkey.decode()),
    }
    r = requests.post(url, headers=header)
    response = r.json()
    print("Status code for new token request: {}".format(r.status_code))
    access_token = response["token"]

    # The expiry on the access token is longer, so we print the token info
    # to a file for later use
    yaml = YAML()
    filecontents = {"access_token": response}
    with open(".abc-access-token.yml", "w") as f:
        yaml.dump(filecontents, f)

    return access_token


def get_refresh_token(installation_id):
    # gets a valid token, or generates a new token if one does not exist
    access_token = None
    # start by looking for valid token info in local file
    token_info = read_token()
    if not token_info:
        print("No access token found; generating new one")
        access_token = _generate_new_token(installation_id)
    else:
        if token_info["expires_at"] < time.ctime(time.time()):
            # if expired, generate a new one
            print("Access token expired; generating new one")
            access_token = _generate_new_token(installation_id)
        else:
            # we can use the existing token
            print("Using existing access token")
            access_token = token_info["token"]
    return access_token


def create_repo(name, token):
    # curl \
    #   -X POST \
    #   -H "Accept: application/vnd.github.v3+json" \
    #   https://api.github.com/orgs/ORG/repos \
    #   -d '{"name":"name"}'
    print("Creating repository {} in org earth-analytics-edu".format(name))
    header = _get_access_token_header(token)
    payload = {"name": name}
    r = requests.post(
        "https://api.github.com/orgs/earth-analytics-edu/repos",
        headers=header,
        json=payload,
    )
    print("Returned ", r.status_code)
    print(r.json())


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "action",
        choices=["installations", "repos", "token", "info", "create"],
        help="""Call GitHub API with app. Choices are installations (list
        installations), repos (test getting public and private repos),
        token (get / refresh access token), info (get info about app),
        create (create a respository).""",
    )
    parser.add_argument(
        "--id",
        dest="installation_id",
        help="""The installation id for generating an access token; use
        installations option to list installations.""",
    )
    parser.add_argument(
        "--repo",
        dest="repo_name",
        help="""The name of the respository to create.""",
    )
    args = parser.parse_args()
    if args.action == "token":
        if args.installation_id is None:
            print(
                """You must specify an installation_id with --id to
            get repos. Use the installations action to list installations."""
            )
        else:
            access_token = get_refresh_token(args.installation_id)

    if args.action == "installations":
        get_installations(True)

    if args.action == "info":
        # /app endpoint
        print("Getting app info")
        encodedkey = generate_jwt()
        header = _get_jwt_header(encodedkey)
        r = requests.get("https://api.github.com/app", headers=header)
        print("Returned ", r.status_code)
        jsonresponse = r.json()
        print(json.dumps(jsonresponse, sort_keys=True, indent=4))

    if args.action == "repos":
        if args.installation_id is None:
            print(
                """You must specify an installation_id with --id to
            get repos. Use the installations action to list installations."""
            )
        else:
            access_token = get_refresh_token(args.installation_id)
            get_repos(access_token)

    if args.action == "create":
        if args.installation_id is None:
            print(
                """You must specify an installation_id with --id to create
                repos. Use the installations action to list installations."""
            )
        else:
            if args.repo_name is None:
                print(
                    """Must specify repo name with --repo to create a
                repository."""
                )
            else:
                access_token = get_refresh_token(args.installation_id)
                create_repo(args.repo_name, access_token)
