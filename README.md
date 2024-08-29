# Simplelogin CLI

A command-line interface for Simplelogin.

## Setup

1. **Install the CLI**  
   Run the following command to install Simplelogin CLI via pip:

   ```sh
   pip install simplelogin
   ```

2. **Set Environmental Variables**  
   To configure the CLI, you'll need to set up two environment variables in your shell:

   - **`SIMPLELOGIN_API_URL`**  
     Define the base URL for the Simplelogin API. You can set it to the default Simplelogin URL or your custom domain.  
     Example:

     ```sh
     export SIMPLELOGIN_API_URL=https://app.simplelogin.io
     ```

   - **`SIMPLELOGIN_EMAIL`**  
     Specify the email address you use to sign in to Simplelogin.  
     Example:
     ```sh
     export SIMPLELOGIN_EMAIL=your-email@example.com
     ```

   **Note:** To make these variables persistent across sessions, add them to your shell's configuration file (e.g., `.bashrc`, `.zshrc`, or `.bash_profile`).

## Capabilities

- [x] **Login to account** (`login`)
  - [x] Supports Multi-Factor Authentication (MFA)
- [x] **Logout** (`logout`)
- [x] **Search aliases** (`alias`)
  - [x] Search using [flags](https://github.com/simple-login/app/blob/master/docs/api.md#get-apiv2aliases) (e.g., `alias --pinned`)
- [x] **Get user stats** (`stats`)
- [x] **Generate custom alias** (`create`)
- [x] **Generate random alias** (`random`)
- [x] **Delete an alias** (`delete`)
- [x] **Disable/enable an alias** (`toggle`)
- [x] **Help** (`--help`) available for all commands
- [x] **Install via pip** (`pip install simplelogin`)
- [x] **Secure API key storage** in the system's [keyring](https://pypi.org/project/keyring/) service 🔑

## Todos

- [ ] Lower the required Python version (currently requires Python 3.12)
- [ ] Add tests
- [ ] Improve commenting
