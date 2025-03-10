# SimpleLogin CLI

A command-line interface for managing your [SimpleLogin](https://simplelogin.io/) email aliases and custom domains.

> Disclaimer: This tool is not officially associated with or endorsed by SimpleLogin. It is an independent, community-developed project that interacts with the SimpleLogin API.

## Overview

SimpleLogin CLI provides a convenient way to manage your SimpleLogin email aliases directly from your terminal. With this tool, you can:

- List, create, toggle, and delete email aliases
- View detailed information about your aliases
- Manage contacts for your aliases
- Manage custom domains 
- View mailboxes associated with your account
- Search and filter your aliases

## Installation

### Prerequisites

- Python 3.6 or higher
- A SimpleLogin account with an API key

### Install via pip

```bash
pip install simplelogin
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/joedemcher/simplelogin-cli.git
   cd simplelogin-cli
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

Before using SimpleLogin CLI, you need to configure your API key:

```bash
simplelogin-cli config set-key YOUR_API_KEY
```

You can create your API key in the SimpleLogin dashboard under API Keys.

Alternatively, you can set the API key as an environment variable:

```bash
export SIMPLELOGIN_API_KEY=YOUR_API_KEY
```

To view your current configuration:

```bash
simplelogin-cli config view
```

## Usage

### Managing Aliases

#### List aliases

```bash
# List all aliases
simplelogin aliases list

# Paginate through aliases
simplelogin aliases list --page=1

# Show only enabled aliases
simplelogin aliases list --enabled

# Show only disabled aliases
simplelogin aliases list --disabled

# Show only pinned aliases
simplelogin aliases list --pinned

# Search aliases
simplelogin aliases list --query="github"
```

#### Create aliases

```bash
# Create a custom alias
simplelogin aliases create custom github
# You'll be prompted to select a suffix and mailbox

# Create a custom alias with options
simplelogin aliases create custom github --note="For GitHub notifications" --name="GitHub"

# Create a random alias
simplelogin aliases create random

# Create a random alias with word mode
simplelogin aliases create random --mode=word

# Create a random alias with a note
simplelogin aliases create random --note="For newsletter signups"
```

#### Manage existing aliases

```bash
# Toggle an alias (enable/disable)
simplelogin aliases toggle 123

# Delete an alias
simplelogin aliases delete 123

# View detailed information about an alias
simplelogin aliases info 123
```

#### Manage contacts

```bash
# List contacts for an alias
simplelogin contacts list 123

# Create a new contact for an alias
simplelogin contacts create 123 user@example.com

# Delete a contact for an alias
simplelogin contacts delete 123

# Toggle a contact (block/unblock)
simplelogin contacts toggle 123
```

### Managing Custom Domains

```bash
# List all custom domains
simplelogin domains list

# View domain details
simplelogin domains info 42

# Update domain settings
simplelogin domains update 42 --catch-all=true --random-prefix=true

# View deleted aliases for a domain
simplelogin domains trash 42
```

### Managing Mailboxes

```bash
# List all mailboxes
simplelogin mailboxes list
```

## Advanced Usage

### Specifying Mailboxes

When creating a custom alias, you can specify which mailboxes should receive emails:

```bash
simplelogin aliases create custom github --mailboxes=1,2,3
```

If you don't specify mailboxes, you'll be prompted to select them interactively.

### Environment Variables

The tool recognizes the following environment variables:

- `SIMPLELOGIN_API_KEY`: Your SimpleLogin API key
- `SIMPLELOGIN_CONFIG`: Custom path to the configuration file
- `XDG_CONFIG_HOME`: Base directory for user-specific configuration files

## Troubleshooting

### Common Issues

1. **API Key errors**: Ensure your API key is correctly set and that it's valid in the SimpleLogin dashboard.

2. **Rate limiting**: SimpleLogin may rate-limit API requests. If you encounter errors, try again after a short delay.

3. **Permissions issues**: Some operations may require a premium SimpleLogin subscription.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [SimpleLogin](https://simplelogin.io/) for their email alias service
- [docopt](http://docopt.org/) for command-line interface parsing
- [tabulate](https://github.com/astanin/python-tabulate) for pretty table formatting
- [questionary](https://github.com/tmbo/questionary) for interactive prompts
