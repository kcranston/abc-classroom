# GitHub Authentication

This directory contains notes and testing scripts for changing our GitHub
authentication for upcoming deprecation of password-based access to the
API; see [GitHub  blog post](https://developer.github.com/changes/2020-02-14-deprecating-password-auth/).

We access git and github functionality two ways in `abc-classroom`:

1. Command-line git operations (e.g. `git commit` or `git clone`)
implemented as python `subprocess` calls in the [`_call_git`](https://github.com/earthlab/abc-classroom/blob/master/abcclassroom/github.py#L19) function. This simply runs with the user's local git setup and SSH keys.
2. GitHub operations, implemented through the GitHub API. These are the ones
that need to change for the upcoming deprecation.

In the [`abc-init`](https://github.com/earthlab/abc-classroom/blob/master/abcclassroom/__main__.py#L35) script, we set up GitHub API api authentication
by authenticating with a username and password, and use that authentication
to generate a personal access token. We save the token to a local file
and read it back in when we make an API call.

The other abc scripts access git and github actions as follows:

`abc-quickstart` : no git or github steps

`abc-new-template` and `abc-update-template` use the following methods:

* init_and_commit : command-line git  
* remote_repo_exists : GitHub API call
* create_repo : GitHub API call
* add_remote : command-line git
* push_to_github : local git action

`abc-clone` uses only command-line git actions (calling `pull_from_github`,
`clone_repo`), as does `abc-feedback` (calling `commit_all_changes` and
`push_to_github`)

So, the two calls that we need to modify are

https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#create-an-organization-repository - requires authentication
https://docs.github.com/en/free-pro-team@latest/rest/reference/repos#get-a-repository - this does not need authentication for public repos, but does
for private repos (which is true in our case)

## Authentication methods

There are two types of authetication methods for a GitHub app. You can
authenticate as the installed app (so actions are done on behalf of the app),
or you can authenticate as a user (so actions are done on behalf of the user).
The `auth-test.py` script has sample code for user authentication and the
`jwt-auth.py` script has sample code for installation authentication.
