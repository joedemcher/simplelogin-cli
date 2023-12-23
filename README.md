# Simplelogin CLI

:construction: Currently a work in progress. :construction:

API key is stored in the system's [keyring service](https://pypi.org/project/keyring/). **Not** plain text.

**Two** environmental variables must be set:

- `SIMPLELOGIN_API_URL`
  - Probably `https://app.simplelogin.io`
- `SIMPLELOGIN_EMAIL`
  - The email you use to sign into Simplelogin

## Capabilities

- [x] Login to account (i.e. `login`)
  - [x] Login with MFA
- [x] Search aliases (i.e. `alias`)
  - [x] Search aliases using [flags](https://github.com/simple-login/app/blob/master/docs/api.md#get-apiv2aliases) (ex. `alias --pinned`)
- [ ] Get user stats (i.e. `stats`)
- [ ] Create new alias (maybe `create`)

## Contributions

If you would like to contribute in any way feel free to open a [pull request](https://github.com/joedemcher/simplelogin-cli/pulls) or suggest something by opening an [issue](https://github.com/joedemcher/simplelogin-cli/issues).

### Development

I am using these tools:

- [Click](https://click.palletsprojects.com/en/8.1.x/)
- [Poetry](https://python-poetry.org/)

#### How to run

1. [Install Poetry if you have not](https://python-poetry.org/docs/#installing-with-pipx)
2. Download this repository
3. Navigate to the base directory
4. Run the command `poetry install`
5. Run the program with `python main.py [COMMAND] [OPTIONS]`
