# Simplelogin CLI

A command line interface for Simplelogin.

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

## Todos

- [ ] Consolidate `auth.py` into `settings.py` :construction:
- [ ] Tests
- [ ] Better commenting

## Contributions

If you would like to contribute in any way feel free to open a [pull request](https://github.com/joedemcher/simplelogin-cli/pulls) or suggest something by opening an [issue](https://github.com/joedemcher/simplelogin-cli/issues).

### How to run

1. [Install Poetry](https://python-poetry.org/docs/#installing-with-pipx)
2. Clone this repository
3. Navigate to the base directory
4. Install the dependencies (`poetry install`)
5. Run the program (`poetry run python simplelogin_cli/main.py`)
