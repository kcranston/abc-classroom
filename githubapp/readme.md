# GitHub Authentication

This directory contains notes and testing scripts for changing our GitHub
authentication for upcoming deprecation of password-based access to the
API; see [GitHub  blog post](https://developer.github.com/changes/2020-02-14-deprecating-password-auth/).

Contents of this directory:

* user_auth.py : collection of functions for user-based authentication
* jwt_auth.py : script to test installation-based authorization
* auth-test.py : script to test various git things with user-based authentication
* test-git-actions.py : testing the abc-template functionalith with user-based authentication

# Existing abc-classroom git actions

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

## Authentication

There are two types of authentication methods for a GitHub app. You can
authenticate as the installed app (so actions are done on behalf of the app),
or you can authenticate as a user (so actions are done on behalf of the user).
The `auth-test.py` script has sample code for user authentication and the
`jwt-auth.py` script has sample code for installation authentication.

Installation-based authentication requires that the app has access to its
private key in order to generate the JSON Web Token (JWT). It is unclear to
me how to handle this with a command-line app that is installed on the user's
computer (with a web-based app, you would have the private key on a server
that is not accessible to the user.)

I've gone with user-based authentication via the device flow process. See the
[GitHub docs for user-based authentication](https://docs.github.com/en/free-pro-team@latest/developers/apps/identifying-and-authorizing-users-for-github-apps).
I am not using expiring user tokens at this point, as this would require the
app to have access to the private key).

The permissions are much more find-grained than with a personal access token.
With a personal access token (the method we are using now), the token allows
you to anything through the API that you can do via the GitHub web interface.

With the GitHub App, you _install_ the app on the organization where you are
going to 'do things' and set the exact permissions that you need. You then
_authenticate_ a user to perform those operations in the organization.
