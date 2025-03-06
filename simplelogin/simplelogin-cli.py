#!/usr/bin/env python3
"""
SimpleLogin CLI - A command line tool for managing SimpleLogin email aliases

Usage:
    simplelogin-cli aliases list
    simplelogin-cli aliases create [--note=<note>] [--prefix=<prefix>] [--suffix=<suffix>] [--mailbox=<mailbox_id>]
    simplelogin-cli aliases toggle <alias_id>
    simplelogin-cli aliases delete <alias_id>
    simplelogin-cli aliases info <alias_id>
    simplelogin-cli domains list
    simplelogin-cli mailboxes list
    simplelogin-cli config set-key <api_key>
    simplelogin-cli config view

Options:
    -h --help                   Show this help
    --version                   Show version
    --note=<note>               Add a note to the alias
    --prefix=<prefix>           Set custom prefix for the alias
    --suffix=<suffix>           Set custom suffix for the alias
    --mailbox=<mailbox_id>      Set specific mailbox ID for the alias
"""

import os
import sys
import json
import requests
import yaml
from docopt import docopt
from tabulate import tabulate
from pathlib import Path

__version__ = '0.1.0'

# API Configuration
BASE_URL = 'https://app.simplelogin.io/api/'

def get_config_dir():
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        config_dir = Path(xdg_config_home) / 'simplelogin'
    else:
        config_dir = Path.home() / '.config' / 'simplelogin'

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file():
    # Also check for environment variable override
    env_config = os.environ.get('SIMPLELOGIN_CONFIG')
    if env_config:
        return Path(env_config)

    return get_config_dir() / 'config.yaml'


def load_config():
    config_file = get_config_file()

    # Check if config file exists, create it if not
    if not config_file.exists():
        default_config = {'api_key': ''}
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f)
        print(f"Config file created at {config_file}")
        print("Please set your API key with: simplelogin-cli config set-key <api_key>")
        sys.exit(0)

    # Load configuration
    with open(config_file, 'r') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            return {}


def save_config(config):
    config_file = get_config_file()
    with open(config_file, 'w') as f:
        yaml.dump(config, f)


def get_headers(config):
    api_key = os.environ.get('SIMPLELOGIN_API_KEY')

    # If not in environment, use config file
    if not api_key:
        api_key = config.get('api_key', '')

    if not api_key:
        print("API key not set. Please use 'simplelogin-cli config set-key <api_key>'")
        print("Or set the SIMPLELOGIN_API_KEY environment variable")
        sys.exit(1)

    return {
        'Authentication': api_key,
        'Content-Type': 'application/json'
    }


# API Functions
def list_aliases(config):
    """List all aliases"""
    headers = get_headers(config)
    response = requests.get(f"{BASE_URL}aliases", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    aliases = response.json()['aliases']

    if not aliases:
        print("No aliases found.")
        return

    table_data = []
    for alias in aliases:
        enabled_status = "✓" if alias['enabled'] else "✗"
        table_data.append([
            alias['id'],
            alias['email'],
            enabled_status,
            alias.get('note', '')
        ])

    print(tabulate(table_data, headers=["ID", "Email", "Enabled", "Note"], tablefmt="grid"))


# ... [other API functions remain the same as before] ...

def set_api_key(config, key):
    """Set the API key in the config file"""
    config['api_key'] = key
    save_config(config)
    print("✓ API key saved successfully")


def view_config(config):
    """View the current configuration"""
    # Check environment variable first
    env_api_key = os.environ.get('SIMPLELOGIN_API_KEY')

    print("Current configuration:")

    if env_api_key:
        # Only show first 4 and last 4 characters of the API key
        masked_key = env_api_key[:4] + '*' * (len(env_api_key) - 8) + env_api_key[-4:]
        print(f"API Key (from environment): {masked_key}")
    elif config.get('api_key'):
        api_key = config['api_key']
        masked_key = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
        print(f"API Key (from config file): {masked_key}")
    else:
        print("API Key: Not set")

    print(f"Config file location: {get_config_file()}")
    print("Environment variables:")
    print("  SIMPLELOGIN_API_KEY: " + ("Set" if env_api_key else "Not set"))
    print("  SIMPLELOGIN_CONFIG: " + (os.environ.get('SIMPLELOGIN_CONFIG', 'Not set')))
    print("  XDG_CONFIG_HOME: " + (os.environ.get('XDG_CONFIG_HOME', 'Not set')))


def main():
    """Main entry point for the CLI"""
    args = docopt(__doc__, version=f"SimpleLogin CLI {__version__}")

    config = load_config()

    # Handle configuration commands
    if args['config']:
        if args['set-key']:
            set_api_key(config, args['<api_key>'])
            return
        elif args['view']:
            view_config(config)
            return


if __name__ == "__main__":
    main()