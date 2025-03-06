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


def create_alias(config, note=None, prefix=None, suffix=None, mailbox_id=None):
    """Create a new alias"""
    headers = get_headers(config)

    data = {}
    if note:
        data['note'] = note
    if prefix:
        data['prefix'] = prefix
    if suffix:
        data['suffix'] = suffix
    if mailbox_id:
        data['mailbox_id'] = mailbox_id

    response = requests.post(
        f"{BASE_URL}aliases",
        headers=headers,
        json=data
    )

    if response.status_code != 201:
        print(f"Error creating alias: {response.status_code} - {response.text}")
        return

    alias = response.json()
    print(f"✓ Alias created: {alias['email']}")
    if 'id' in alias:
        print(f"  ID: {alias['id']}")
    if note:
        print(f"  Note: {note}")


def toggle_alias(config, alias_id):
    """Toggle an alias on/off"""
    headers = get_headers(config)

    response = requests.get(f"{BASE_URL}aliases/{alias_id}", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    alias = response.json()
    current_status = alias['enabled']

    response = requests.post(
        f"{BASE_URL}aliases/{alias_id}/toggle",
        headers=headers
    )

    if response.status_code != 200:
        print(f"Error toggling alias: {response.status_code} - {response.text}")
        return

    new_status = "enabled" if not current_status else "disabled"
    print(f"✓ Alias {alias['email']} is now {new_status}")


def delete_alias(config, alias_id):
    """Delete an alias"""
    headers = get_headers(config)

    response = requests.get(f"{BASE_URL}aliases/{alias_id}", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    alias_email = response.json()['email']

    confirm = input(f"Are you sure you want to delete {alias_email}? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    response = requests.delete(
        f"{BASE_URL}aliases/{alias_id}",
        headers=headers
    )

    if response.status_code != 200:
        print(f"Error deleting alias: {response.status_code} - {response.text}")
        return

    print(f"✓ Alias {alias_email} deleted successfully")


def alias_info(config, alias_id):
    """Show detailed information about an alias"""
    headers = get_headers(config)
    response = requests.get(f"{BASE_URL}aliases/{alias_id}", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    alias = response.json()

    print(f"Alias: {alias['email']}")
    print(f"ID: {alias['id']}")
    print(f"Creation date: {alias.get('creation_date', 'N/A')}")
    print(f"Enabled: {'Yes' if alias['enabled'] else 'No'}")

    if 'note' in alias and alias['note']:
        print(f"Note: {alias['note']}")

    if 'mailbox' in alias:
        print(f"Mailbox: {alias['mailbox']['email']}")

    if 'nb_forward' in alias:
        print(f"Forwarded emails: {alias['nb_forward']}")

    if 'nb_reply' in alias:
        print(f"Reply emails: {alias['nb_reply']}")

    if 'nb_block' in alias:
        print(f"Blocked emails: {alias['nb_block']}")


def list_domains(config):
    """List all domains"""
    headers = get_headers(config)
    response = requests.get(f"{BASE_URL}domains", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    domains = response.json()['domains']

    if not domains:
        print("No domains found.")
        return

    table_data = []
    for domain in domains:
        table_data.append([
            domain['id'],
            domain['domain'],
            domain.get('creation_date', 'N/A'),
            domain.get('nb_alias', 0)
        ])

    print(tabulate(table_data, headers=["ID", "Domain", "Creation Date", "# Aliases"], tablefmt="grid"))


def list_mailboxes(config):
    """List all mailboxes"""
    headers = get_headers(config)
    response = requests.get(f"{BASE_URL}mailboxes", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    mailboxes = response.json()['mailboxes']

    if not mailboxes:
        print("No mailboxes found.")
        return

    table_data = []
    for mailbox in mailboxes:
        default_status = "✓" if mailbox.get('default', False) else ""
        table_data.append([
            mailbox['id'],
            mailbox['email'],
            default_status,
            mailbox.get('creation_date', 'N/A')
        ])

    print(tabulate(table_data, headers=["ID", "Email", "Default", "Creation Date"], tablefmt="grid"))


def set_api_key(config, key):
    """Set the API key in the config file"""
    config['api_key'] = key
    save_config(config)
    print("✓ API key saved successfully")


def view_config(config):
    """View the current configuration"""
    env_api_key = os.environ.get('SIMPLELOGIN_API_KEY')

    print("Current configuration:")

    if env_api_key:
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

    if args['config']:
        if args['set-key']:
            set_api_key(config, args['<api_key>'])
            return
        elif args['view']:
            view_config(config)
            return

    if args['aliases']:
        if args['list']:
            list_aliases(config)
            return
        elif args['create']:
            create_alias(
                config,
                note=args['--note'],
                prefix=args['--prefix'],
                suffix=args['--suffix'],
                mailbox_id=args['--mailbox']
            )
            return
        elif args['toggle']:
            toggle_alias(config, args['<alias_id>'])
            return
        elif args['delete']:
            delete_alias(config, args['<alias_id>'])
            return
        elif args['info']:
            alias_info(config, args['<alias_id>'])
            return

    elif args['domains'] and args['list']:
        list_domains(config)
        return

    elif args['mailboxes'] and args['list']:
        list_mailboxes(config)
        return

    print("Command not recognized. Use --help to see available commands.")


if __name__ == "__main__":
    main()