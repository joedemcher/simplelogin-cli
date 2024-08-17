# Simplelogin CLI

A command line interface for Simplelogin.

## Setup

1. Install the CLI with the following command: `pip install simplelogin`

2. Set two environmental variables in your shell:
  - `SIMPLELOGIN_API_URL`
    - https://app.simplelogin.io or your domain.
  - `SIMPLELOGIN_EMAIL`
    - The email you use to sign in to Simplelogin.


## Capabilities

- [x] Login to account (`login`)
  - [x] Login with MFA
- [x] Logout (`logout`)
- [x] Search aliases (`alias`)
  - [x] Search aliases using [flags](https://github.com/simple-login/app/blob/master/docs/api.md#get-apiv2aliases) (ex. `alias --pinned`)
- [x] Get user stats (`stats`)
- [x] Generate custom alias (`create`)
- [x] Generate random alias (`random`)
- [x] Delete an alias (`delete`)
- [x] Disable/enable an alias (`toggle`)
- [x] `--help` available for all commands
- [x] Installable via `pip install simplelogin`
- [x] API key stored securely in the system's [keyring](https://pypi.org/project/keyring/) service 🔑

## Todos

- [ ] Bring down the required Python version (currently requires Python 3.12 for no good reason)
- [ ] Tests
- [ ] Better commenting
