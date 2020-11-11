# test the git actions required for the template script

import shutil
from pathlib import Path

import user_auth as auth
from abcclassroom import github

if __name__ == "__main__":
    organization = "earth-analytics-edu"

    # create local dir
    repo_name = Path("test-repo-abc-bot")
    dir_exists = repo_name.is_dir()
    if not dir_exists:
        repo_name.mkdir()

    # copy test files into local dir
    test_files = Path("test_files")
    for f in test_files.iterdir():
        print(" {}".format(f))
        shutil.copy(f, repo_name)

    # init and commit the dir
    github.init_and_commit(repo_name, True)
    github.master_branch_to_main(repo_name)

    # get github token
    token = auth.get_access_token()

    # create remote repo
    remote_exists = github.remote_repo_exists(organization, repo_name, token)
    if remote_exists:
        print("remote repo {}/{} exists".format(organization, repo_name))
    else:
        print(
            "remote repo {}/{} does not exist".format(organization, repo_name)
        )

    # add remote
    try:
        github.add_remote(repo_name, organization, repo_name)
    except RuntimeError:
        print("Remote already added to local repository")
        pass

    # push to github
    try:
        github.push_to_github(repo_name, "main")
    except RuntimeError as e:
        print(
            """Push to github failed. This is often because there are
            changes on the remote that you do not have locally. Here is the
            github error:"""
        )
        print(e)
