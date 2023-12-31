# Simplelogin CLI

:construction: Currently a work in progress :construction:

- The API key is stored securely in the system's [keyring service](https://pypi.org/project/keyring/) :key:

- **Two** environmental variables must be set:

  - `SIMPLELOGIN_API_URL`
    - `https://app.simplelogin.io` or your domain.
  - `SIMPLELOGIN_EMAIL`
    - The email you use to sign into Simplelogin.

## Capabilities

- [x] Login to account (`login`)
  - [x] Login with MFA
- [ ] Logout (`logout`) :construction:
- [x] Search aliases (`alias`) (rate limit keeps getting reached, any ideas?)
  - [x] Search aliases using [flags](https://github.com/simple-login/app/blob/master/docs/api.md#get-apiv2aliases) (ex. `alias --pinned`)
- [x] Get user stats (`stats`)
- [x] Generate custom alias (`create`)
- [x] Generate random alias (`random`)
- [x] Delete an alias (`delete`)
- [x] Toggle an alias (`toggle`)
- [x] `--help` available for all commands

## Contributions

If you would like to contribute in any way feel free to open a [pull request](https://github.com/joedemcher/simplelogin-cli/pulls) or suggest something by opening an [issue](https://github.com/joedemcher/simplelogin-cli/issues).

### Development

I am using these tools:

- [Click](https://click.palletsprojects.com/en/8.1.x/)
- [Poetry](https://python-poetry.org/)

_But I'm not sure if they're overkill?_ :woozy_face:

#### How to run

1. [Install Poetry if you have not](https://python-poetry.org/docs/#installing-with-pipx)
2. Download this repository
3. Navigate to the base directory
4. Run the command `poetry install`
5. Run the program with `python simplelogin_cli/main.py`
