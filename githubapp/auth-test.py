# Testing user-to-server authentication tokens. Used to perform
# actions on behalf of users
# See https://docs.github.com/en/free-pro-team@latest/developers/apps/
# identifying-and-authorizing-users-for-github-apps

import sys
import requests

import user_auth


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

    payload = {"title": "use git core.editor, if set"}
    r = requests.patch(
        "https://api.github.com/repos/earthlab/abc-classroom/issues/311",
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


def list_org_issues(org, token):
    # GET /orgs/{org}/issues
    # get issues assigned to authenticated user
    r = requests.get(
        "https://api.github.com/orgs/{}/issues".format(org),
        headers=get_auth_header(token),
    )
    print(r.status_code)
    print(r.json())


def list_orgs(token):
    # GET /user/orgs
    r = requests.get(
        "https://api.github.com/user/orgs", headers=get_auth_header(token)
    )
    print(r.status_code)
    print(r.json())


def list_repos(token):
    # GET /user/repos
    r = requests.get(
        "https://api.github.com/user/repos", headers=get_auth_header(token)
    )
    print(r.status_code)
    response = r.json()
    print("Found {} repos".format(len(response)))
    for repo in response:
        print(repo["full_name"])


def create_repo(org, name, token):
    # curl \
    #   -X POST \
    #   -H "Accept: application/vnd.github.v3+json" \
    #   https://api.github.com/orgs/ORG/repos \
    #   -d '{"name":"name"}'
    print("Creating repository {} in org {}".format(name, org))
    header = get_auth_header(token)
    payload = {"name": name}
    r = requests.post(
        "https://api.github.com/orgs/{}/repos".format(org),
        headers=header,
        json=payload,
    )
    print("Returned ", r.status_code)
    print(r.json())


def get_resource(url, token, printresponse=False):
    r = requests.get(url, headers=get_auth_header(token))
    if printresponse:
        print(r.json())
    return r.status_code


if __name__ == "__main__":

    # There are three steps:
    # Check for presence of authorization info in the file .abc-tokens.yaml
    # If the file does not exist, start by getting a login code for the user
    # If authorization info exists, check that the access_token is present
    # If it is not present, poll for an access code using the device code
    # If we have a valid access_token, then call the API using that token

    token = user_auth.get_access_token()
    if token is None:
        sys.exit(1)

    print("Testing getting public private repos")
    test_repos = [
        {"repo_name": "hub-ops", "organization": "earthlab"},
        {
            "repo_name": "spring-2020-eapython-nbgrader",
            "organization": "earth-analytics-edu",
        },
        {"repo_name": "nbgrader-bootcamp", "organization": "earthlab"},
    ]
    for repo in test_repos:
        repo_name = repo["repo_name"]
        org = repo["organization"]
        url = "https://api.github.com/repos/{}/{}".format(org, repo_name)
        if get_resource(url, token) == 200:
            print(" repo {} exists!".format(repo_name))
        else:
            print(" no repo {} :(".format(repo_name))

    list_repos(token)

    get_resource("https://api.github.com/user/installations", token)
    get_resource("https://api.github.com/user/orgs", token)

    # list_orgs(token)
    # list_org_issues("earthlab",token)
    # update_issue(token)
    # create_repo('earth-analytics-edu','test-repo2',token)
