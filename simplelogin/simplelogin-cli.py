#!/usr/bin/env python3
"""
SimpleLogin CLI - A command line tool for managing SimpleLogin email aliases

Usage:
    simplelogin-cli aliases list [--page=<page>] [--pinned] [--disabled] [--enabled] [--query=<query>]
    simplelogin-cli aliases create [--note=<note>] [--prefix=<prefix>] [--suffix=<suffix>] [--mailbox=<mailbox_id>]
    simplelogin-cli aliases toggle <alias_id>
    simplelogin-cli aliases delete <alias_id>
    simplelogin-cli aliases info <alias_id>
    simplelogin-cli domains list
    simplelogin-cli domains info <domain_id>
    simplelogin-cli domains update <domain_id> [--catch-all=<bool>] [--random-prefix=<bool>] [--name=<name>] [--mailboxes=<ids>]
    simplelogin-cli domains trash <domain_id>
    simplelogin-cli mailboxes list
    simplelogin-cli config set-key <api_key>
    simplelogin-cli config view

Options:
    -h --help                    Show this help
    --version                    Show version
    --page=<page>                Page number (starts at 0) [default: 0]
    --pinned                     Show only pinned aliases
    --disabled                   Show only disabled aliases
    --enabled                    Show only enabled aliases
    --query=<query>              Search aliases
    --note=<note>                Add a note to the alias
    --prefix=<prefix>            Set custom prefix for the alias
    --suffix=<suffix>            Set custom suffix for the alias
    --mailbox=<mailbox_id>       Set specific mailbox ID for the alias
    --catch-all=<bool>           Enable/disable catch-all for domain (true/false)
    --random-prefix=<bool>       Enable/disable random prefix generation (true/false)
    --name=<name>                Set a name for the domain
    --mailboxes=<ids>            Comma-separated list of mailbox IDs
"""

import os
import sys
import json
import requests
import yaml
from docopt import docopt
from tabulate import tabulate
from pathlib import Path
from datetime import datetime

__version__ = '0.1.0'

# API Configuration
BASE_URL = 'https://app.simplelogin.io/api/'


# Configuration setup following XDG Base Directory Specification
def get_config_dir():
    """Get the configuration directory following XDG standards"""
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        config_dir = Path(xdg_config_home) / 'simplelogin'
    else:
        config_dir = Path.home() / '.config' / 'simplelogin'

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file():
    """Get the path to the configuration file"""
    # Also check for environment variable override
    env_config = os.environ.get('SIMPLELOGIN_CONFIG')
    if env_config:
        return Path(env_config)

    return get_config_dir() / 'config.yaml'


def load_config():
    """Load configuration from file"""
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
    """Save configuration to file"""
    config_file = get_config_file()
    with open(config_file, 'w') as f:
        yaml.dump(config, f)


def get_headers(config):
    """Get API headers with authentication"""
    # First check environment variable for API key
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


def format_datetime(timestamp_str):
    """Format datetime string to a more readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('+00:00', '+0000'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str


# API Functions
def list_aliases(config, page=0, pinned=False, disabled=False, enabled=False, query=None):
    """
    List aliases with pagination and filtering support

    Args:
        config: Configuration dictionary
        page: Page number (starts at 0)
        pinned: Show only pinned aliases
        disabled: Show only disabled aliases
        enabled: Show only enabled aliases
        query: Search query
    """
    headers = get_headers(config)
    params = {'page_id': page}

    # Add filters (only one can be active)
    if pinned:
        params['pinned'] = True
    elif disabled:
        params['disabled'] = True
    elif enabled:
        params['enabled'] = True

    # Add search query if provided
    data = {'query': query} if query else None

    response = requests.get(
        f"{BASE_URL}v2/aliases",
        headers=headers,
        params=params,
        json=data
    )

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
        pinned_status = "📌" if alias.get('pinned', False) else ""

        # Format latest activity
        latest = alias.get('latest_activity', {})
        activity = f"{latest.get('action', 'N/A')} ({format_datetime(str(latest.get('timestamp', '')))}" if latest else "N/A"

        # Get primary mailbox
        mailbox = alias['mailboxes'][0]['email'] if alias.get('mailboxes') else 'N/A'

        table_data.append([
            alias['id'],
            alias['email'],
            alias.get('name', ''),
            enabled_status,
            pinned_status,
            mailbox,
            activity,
            f"F:{alias.get('nb_forward', 0)} R:{alias.get('nb_reply', 0)} B:{alias.get('nb_block', 0)}",
            alias.get('note', '')
        ])

    print(tabulate(
        table_data,
        headers=["ID", "Email", "Name", "Enabled", "Pinned", "Mailbox", "Latest Activity", "Stats", "Note"],
        tablefmt="grid"
    ))

    # Indicate if there might be more pages
    if len(aliases) == 20:
        print(f"\nShowing page {page}. Use --page to see more results.")


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

    # First, get current status
    response = requests.get(f"{BASE_URL}aliases/{alias_id}", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    alias = response.json()
    current_status = alias['enabled']

    # Now toggle
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

    # First, get the alias to show what we're deleting
    response = requests.get(f"{BASE_URL}aliases/{alias_id}", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    alias_email = response.json()['email']

    # Confirm deletion
    confirm = input(f"Are you sure you want to delete {alias_email}? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    # Now delete
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
    """List all custom domains"""
    headers = get_headers(config)
    response = requests.get(f"{BASE_URL}custom_domains", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    domains = response.json()

    if not domains:
        print("No custom domains found.")
        return

    table_data = []
    for domain in domains:
        verified_status = "✓" if domain.get('is_verified', False) else "✗"
        catch_all_status = "✓" if domain.get('catch_all', False) else "✗"

        table_data.append([
            domain['id'],
            domain['domain_name'],
            verified_status,
            catch_all_status,
            domain.get('nb_alias', 0)
        ])

    print(tabulate(table_data, headers=["ID", "Domain", "Verified", "Catch-All", "# Aliases"], tablefmt="grid"))


def domain_info(config, domain_id):
    """Show detailed information about a custom domain"""
    headers = get_headers(config)
    # Note: There's no specific endpoint for getting a single domain by ID,
    # so we'll get all domains and filter for the one we want
    response = requests.get(f"{BASE_URL}custom_domains", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    domains = response.json()
    domain = next((d for d in domains if str(d['id']) == domain_id), None)

    if not domain:
        print(f"Domain with ID {domain_id} not found.")
        return

    print(f"Domain: {domain['domain_name']}")
    print(f"ID: {domain['id']}")
    print(f"Name: {domain.get('name', 'N/A')}")
    print(f"Creation date: {format_datetime(domain.get('creation_date', 'N/A'))}")
    print(f"Verified: {'Yes' if domain.get('is_verified', False) else 'No'}")
    print(f"Catch-all: {'Enabled' if domain.get('catch_all', False) else 'Disabled'}")
    print(f"Random prefix generation: {'Enabled' if domain.get('random_prefix_generation', False) else 'Disabled'}")
    print(f"Number of aliases: {domain.get('nb_alias', 0)}")

    if 'mailboxes' in domain and domain['mailboxes']:
        print("\nLinked mailboxes:")
        for mailbox in domain['mailboxes']:
            print(f"  - {mailbox['email']} (ID: {mailbox['id']})")
    else:
        print("\nNo mailboxes linked to this domain.")


def update_domain(config, domain_id, catch_all=None, random_prefix=None, name=None, mailboxes=None):
    """Update a custom domain's settings"""
    headers = get_headers(config)

    data = {}
    if catch_all is not None:
        data['catch_all'] = catch_all.lower() == 'true'
    if random_prefix is not None:
        data['random_prefix_generation'] = random_prefix.lower() == 'true'
    if name is not None:
        data['name'] = name
    if mailboxes is not None:
        # Split the comma-separated string into a list of integers
        try:
            data['mailbox_ids'] = [int(id.strip()) for id in mailboxes.split(',')]
        except ValueError:
            print("Error: Mailbox IDs must be comma-separated integers.")
            return

    if not data:
        print("No changes specified. Use --catch-all, --random-prefix, --name, or --mailboxes.")
        return

    response = requests.patch(
        f"{BASE_URL}custom_domains/{domain_id}",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        print(f"Error updating domain: {response.status_code} - {response.text}")
        return

    print(f"✓ Domain updated successfully")
    # Display the updated domain info
    domain_info(config, domain_id)


def domain_trash(config, domain_id):
    """Show deleted aliases for a custom domain"""
    headers = get_headers(config)
    response = requests.get(f"{BASE_URL}custom_domains/{domain_id}/trash", headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    trash_data = response.json()
    aliases = trash_data.get('aliases', [])

    if not aliases:
        print("No deleted aliases found for this domain.")
        return

    table_data = []
    for alias in aliases:
        # Convert timestamp to readable date if available
        deleted_at = datetime.fromtimestamp(alias['deletion_timestamp']).strftime('%Y-%m-%d %H:%M:%S') \
            if 'deletion_timestamp' in alias else 'N/A'

        table_data.append([
            alias['alias'],
            deleted_at
        ])

    print(tabulate(table_data, headers=["Alias", "Deleted At"], tablefmt="grid"))


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

    # Handle aliases commands
    if args['aliases']:
        if args['list']:
            list_aliases(
                config,
                page=int(args.get('--page', 0)),
                pinned=args['--pinned'],
                disabled=args['--disabled'],
                enabled=args['--enabled'],
                query=args.get('--query')
            )
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

    # Handle domains commands
    elif args['domains']:
        if args['list']:
            list_domains(config)
            return
        elif args['info']:
            domain_info(config, args['<domain_id>'])
            return
        elif args['update']:
            update_domain(
                config,
                args['<domain_id>'],
                catch_all=args['--catch-all'],
                random_prefix=args['--random-prefix'],
                name=args['--name'],
                mailboxes=args['--mailboxes']
            )
            return
        elif args['trash']:
            domain_trash(config, args['<domain_id>'])
            return

    # Handle mailboxes commands
    elif args['mailboxes'] and args['list']:
        list_mailboxes(config)
        return

    # If we get here, no known command was properly handled
    print("Command not recognized. Use --help to see available commands.")


if __name__ == "__main__":
    main()