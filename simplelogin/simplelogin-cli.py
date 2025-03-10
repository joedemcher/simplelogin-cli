#!/usr/bin/env python3
"""
SimpleLogin CLI - A command line tool for managing SimpleLogin email aliases

Usage:
    simplelogin aliases list [--page=<page>] [--pinned] [--disabled] [--enabled] [--query=<query>]
    simplelogin aliases create custom <prefix> [--mailboxes=<ids>] [--note=<note>] [--name=<name>]
    simplelogin aliases create random [--mode=<mode>] [--note=<note>]
    simplelogin aliases toggle <alias_id>
    simplelogin aliases delete <alias_id>
    simplelogin aliases info <alias_id>
    simplelogin contacts list <alias_id>
    simplelogin contacts create <alias_id> <contact>
    simplelogin contacts delete <contact_id>
    simplelogin contacts toggle <contact_id>
    simplelogin domains list
    simplelogin domains info <domain_id>
    simplelogin domains update <domain_id> [--catch-all=<bool>] [--random-prefix=<bool>] [--name=<name>] [--mailboxes=<ids>]
    simplelogin domains trash <domain_id>
    simplelogin mailboxes list
    simplelogin config set-key <api_key>
    simplelogin config view

Options:
    -h --help                    Show this help
    --version                    Show version
    --page=<page>                Page number (starts at 0) [default: 0]
    --pinned                     Show only pinned aliases
    --disabled                   Show only disabled aliases
    --enabled                    Show only enabled aliases
    --query=<query>              Search aliases
    --name=<name>                Set a name for the alias or domain
    --mode=<mode>                Random alias mode (uuid or word)
    --note=<note>                Add a note to the alias
    --catch-all=<bool>           Enable/disable catch-all for domain (true/false)
    --random-prefix=<bool>       Enable/disable random prefix generation (true/false)
    --mailboxes=<ids>            Comma-separated list of mailbox IDs
"""

import os
import sys

import requests
import yaml
from docopt import docopt
from tabulate import tabulate
from pathlib import Path
from datetime import datetime
import questionary as q

__version__ = '0.2.3'

# API Configuration
BASE_URL = 'https://app.simplelogin.io'


def get_config_dir():
    """Get the configuration directory following XDG standards"""
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        config_dir = Path(xdg_config_home) / 'simplelogin'
    else:
        config_dir = Path.home() / '.config' / 'simplelogin'

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file():
    """Get the path to the configuration file"""
    env_config = os.environ.get('SIMPLELOGIN_CONFIG')
    if env_config:
        return Path(env_config)

    return get_config_dir() / 'config.yaml'


def load_config():
    """Load configuration from file"""
    config_file = get_config_file()

    if not config_file.exists():
        default_config = {'api_key': ''}
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f)
        print(f"Config file created at {config_file}")
        print("Please set your API key with: simplelogin config set-key <api_key>")
        sys.exit(0)

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
    api_key = os.environ.get('SIMPLELOGIN_API_KEY')

    if not api_key:
        api_key = config.get('api_key', '')

    if not api_key:
        print("API key not set. Please use 'simplelogin config set-key <api_key>'")
        print("Or set the SIMPLELOGIN_API_KEY environment variable")
        sys.exit(1)

    return {
        'Authentication': f"{api_key}",
        'Content-Type': 'application/json'
    }


def format_datetime(timestamp_str):
    """Format datetime string to a more readable format"""
    if not timestamp_str:
        return "N/A"

    try:
        if isinstance(timestamp_str, str):
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', '+0000'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(timestamp_str, (int, float)):
            dt = datetime.fromtimestamp(timestamp_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
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

    if pinned:
        params['pinned'] = True
    elif disabled:
        params['disabled'] = True
    elif enabled:
        params['enabled'] = True

    data = {'query': query} if query else None

    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/aliases",
            headers=headers,
            params=params,
            json=data,
            timeout=10
        )

        response.raise_for_status()

        aliases = response.json()['aliases']

        if not aliases:
            print("No aliases found.")
            return

        table_data = []
        for alias in aliases:
            enabled_status = "✓" if alias['enabled'] else "❌"
            pinned_status = "📌" if alias.get('pinned', False) else ""

            latest = alias.get('latest_activity', {})
            activity = f"{latest.get('action', 'N/A')} ({format_datetime(latest.get('timestamp', ''))})" if latest else "N/A"

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

        if len(aliases) == 20:
            print(f"\nShowing page {page}. Use --page to see more results.")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SimpleLogin API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def get_alias_options(config):
    """Get available options for creating new aliases"""
    headers = get_headers(config)
    params = {}

    try:
        response = requests.get(
            f"{BASE_URL}/api/v5/alias/options",
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error getting alias options: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")
        return None


def create_custom_alias(config, prefix, mailbox_ids=None, note=None, name=None):
    """
    Create a new custom alias

    Args:
        config: Configuration dictionary
        prefix: Alias prefix
        mailbox_ids: List of mailbox IDs
        note: Optional note
        name: Optional name
    """
    options = get_alias_options(config)
    if not options:
        return

    if not options['can_create']:
        print("You cannot create new aliases at this time.")
        return

    suffixes = options['suffixes']
    suffix_ids = {}

    for suffix in suffixes:
        suffix_ids[suffix['suffix']] = suffix['signed_suffix']

    if not suffix_ids:
        print("No available suffixes found.")
        return

    suffix_key = q.select(
        "Select your email suffix",
        choices=[key for key in suffix_ids.keys()],
    ).ask()

    headers = get_headers(config)
    data = {'alias_prefix': prefix, 'signed_suffix': suffix_ids.get(suffix_key)}

    if mailbox_ids:
        data['mailbox_ids'] = mailbox_ids

    if note:
        data['note'] = note
    if name:
        data['name'] = name

    try:
        response = requests.post(
            f"{BASE_URL}/api/v3/alias/custom/new",
            headers=headers,
            json=data,
            timeout=10
        )

        response.raise_for_status()

        alias = response.json()
        print(f"✓ Custom alias created: {alias['email']}")
        print(f"  ID: {alias['id']}")
        if note:
            print(f"  Note: {note}")
        if name:
            print(f"  Name: {name}")

    except requests.exceptions.RequestException as e:
        print(f"Error creating alias: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def create_random_alias(config, mode=None, note=None):
    """
    Create a new random alias

    Args:
        config: Configuration dictionary
        mode: Either 'uuid' or 'word' (optional)
        note: Optional note
    """
    headers = get_headers(config)
    params = {}
    if mode:
        if mode not in ('uuid', 'word'):
            print("Mode must be either 'uuid' or 'word'")
            return
        params['mode'] = mode

    data = {}
    if note:
        data['note'] = note

    try:
        response = requests.post(
            f"{BASE_URL}/api/alias/random/new",
            headers=headers,
            json=data,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        alias = response.json()
        print(f"✓ Random alias created: {alias['email']}")
        print(f"  ID: {alias['id']}")
        if note:
            print(f"  Note: {note}")

    except requests.exceptions.RequestException as e:
        print(f"Error creating random alias: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def toggle_alias(config, alias_id):
    """Toggle an alias on/off"""
    headers = get_headers(config)

    try:
        # First, get current status
        response = requests.get(
            f"{BASE_URL}/api/aliases/{alias_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        alias = response.json()
        current_status = alias['enabled']

        toggle_response = requests.post(
            f"{BASE_URL}/api/aliases/{alias_id}/toggle",
            headers=headers,
            timeout=10
        )
        toggle_response.raise_for_status()

        new_status = "enabled" if not current_status else "disabled"
        print(f"✓ Alias {alias['email']} is now {new_status}")

    except requests.exceptions.RequestException as e:
        print(f"Error toggling alias: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def delete_alias(config, alias_id):
    """Delete an alias"""
    headers = get_headers(config)

    try:
        response = requests.get(
            f"{BASE_URL}/api/aliases/{alias_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        alias_email = response.json()['email']

        confirm = input(f"Are you sure you want to delete {alias_email}? (y/n): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return

        delete_response = requests.delete(
            f"{BASE_URL}/api/aliases/{alias_id}",
            headers=headers,
            timeout=10
        )
        delete_response.raise_for_status()

        print(f"✓ Alias {alias_email} deleted successfully")

    except requests.exceptions.RequestException as e:
        print(f"Error deleting alias: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def alias_info(config, alias_id):
    """Show detailed information about an alias"""
    headers = get_headers(config)

    try:
        response = requests.get(
            f"{BASE_URL}/api/aliases/{alias_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        alias = response.json()

        print(f"Alias: {alias['email']}")
        print(f"ID: {alias['id']}")
        print(f"Creation date: {format_datetime(alias.get('creation_date', 'N/A'))}")
        print(f"Enabled: {'Yes' if alias['enabled'] else 'No'}")

        if 'note' in alias and alias['note']:
            print(f"Note: {alias['note']}")

        if 'mailboxes' in alias and alias['mailboxes']:
            print("\nMailboxes:")
            for mailbox in alias['mailboxes']:
                print(f"  - {mailbox['email']} (ID: {mailbox['id']})")
        elif 'mailbox' in alias:
            print(f"Mailbox: {alias['mailbox']['email']}")

        if 'nb_forward' in alias:
            print(f"Forwarded emails: {alias['nb_forward']}")

        if 'nb_reply' in alias:
            print(f"Reply emails: {alias['nb_reply']}")

        if 'nb_block' in alias:
            print(f"Blocked emails: {alias['nb_block']}")

    except requests.exceptions.RequestException as e:
        print(f"Error getting alias info: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")

def list_contacts(config, alias_id, page=0):
    """ List contacts for an alias """
    headers = get_headers(config)
    params = {'page_id': page, 'alias_id': alias_id}

    try:
        response = requests.get(
            f"{BASE_URL}/api/aliases/{alias_id}/contacts",
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        contacts = response.json()['contacts']

        if not contacts:
            print("No contacts found.")
            return

        table_data = []
        for contact in contacts:

            block_forward =  "✓" if contact.get('block_forward', True) else "✗"

            table_data.append([
                contact['id'],
                contact['contact'],
                contact['reverse_alias'],
                format_datetime(contact['last_email_sent_date']),
                block_forward
            ])

        print(tabulate(
            table_data,
            headers=["ID", "Contact", "Reverse Alias", "Last Email Sent", "Block Forward"],
            tablefmt="grid"
        ))

        if len(contacts) == 20:
            print(f"\nShowing page {page}. Use --page to see more results.")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SimpleLogin API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")

def create_contact(config, alias_id, contact):
    """ Create a new contact for an alias """
    headers = get_headers(config)
    data = {"contact" : contact}

    try:
        response = requests.post(
            f"{BASE_URL}/api/aliases/{alias_id}/contacts",
            headers=headers,
            timeout=10,
            json=data
        )
        response.raise_for_status()

        contact = response.json()

        if contact['existed']:
            print("  Contact already exists.")
        else:
            print(f"  ✓ Contact created")
        print(f"  ID: {contact['id']}")
        print(f"  Reverse alias: {contact['reverse_alias']}")

    except requests.exceptions.RequestException as e:
        print(f"Error creating contact: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")

def delete_contact(config, contact_id):
    """ Delete a contact for an alias """
    headers = get_headers(config)

    try:
        response = requests.delete(
            f"{BASE_URL}/api/contacts/{contact_id}",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        delete_response = response.json()

        if delete_response['deleted']:
            print("✓ Contact deleted successfully")
        else:
            print(" Contact not found")

    except requests.exceptions.RequestException as e:
        print(f"Error deleting contact: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")

def toggle_contact(config, contact_id):
    """ Delete a contact for an alias """
    headers = get_headers(config)

    try:
        response = requests.post(
            f"{BASE_URL}/api/contacts/{contact_id}/toggle",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        toggle_response = response.json()

        new_status = "unblocked" if not toggle_response['block_forward'] else "blocked"
        print(f"  Contact has been {new_status}")


    except requests.exceptions.RequestException as e:
        print(f"Error toggling contact: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")

def list_domains(config):
    """List all custom domains"""
    headers = get_headers(config)

    try:
        response = requests.get(
            f"{BASE_URL}/api/custom_domains",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        domains = response.json()['custom_domains']

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

    except requests.exceptions.RequestException as e:
        print(f"Error listing domains: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def domain_info(config, domain_id):
    """Show detailed information about a custom domain"""
    headers = get_headers(config)

    try:
        response = requests.get(
            f"{BASE_URL}/api/custom_domains",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        domains = response.json()['custom_domains']
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

    except requests.exceptions.RequestException as e:
        print(f"Error getting domain info: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


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
        try:
            data['mailbox_ids'] = [int(id.strip()) for id in mailboxes.split(',')]
        except ValueError:
            print("Error: Mailbox IDs must be comma-separated integers.")
            return

    if not data:
        print("No changes specified. Use --catch-all, --random-prefix, --name, or --mailboxes.")
        return

    try:
        response = requests.patch(
            f"{BASE_URL}/api/custom_domains/{domain_id}",
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()

        print(f"✓ Domain updated successfully")
        domain_info(config, domain_id)

    except requests.exceptions.RequestException as e:
        print(f"Error updating domain: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def domain_trash(config, domain_id):
    """Show deleted aliases for a custom domain"""
    headers = get_headers(config)

    try:
        response = requests.get(
            f"{BASE_URL}/api/custom_domains/{domain_id}/trash",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        trash_data = response.json()
        aliases = trash_data.get('aliases', [])

        if not aliases:
            print("No deleted aliases found for this domain.")
            return

        table_data = []
        for alias in aliases:
            deleted_at = format_datetime(alias.get('deletion_timestamp'))

            table_data.append([
                alias['alias'],
                deleted_at
            ])

        print(tabulate(table_data, headers=["Alias", "Deleted At"], tablefmt="grid"))

    except requests.exceptions.RequestException as e:
        print(f"Error getting domain trash: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")


def get_mailboxes(config):
    headers = get_headers(config)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/mailboxes",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        mailboxes = response.json()["mailboxes"]

        if not mailboxes:
            print("No mailboxes found.")
            return []

        return mailboxes

    except requests.exceptions.RequestException as e:
        print(f"Error getting mailboxes: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error message: {error_data.get('error')}")
            except:
                print(f"Error message: {e.response.text}")
        return []


def select_mailboxes(config):
    """Prompts the user to choose their mailbox(es) for alias generation."""
    mailboxes = get_mailboxes(config)
    if not mailboxes:
        print("Unable to retrieve mailboxes. Please try again later.")
        return []

    mailbox_ids = {}

    for mailbox in mailboxes:
        mailbox_ids[mailbox["email"]] = mailbox["id"]

    if not mailbox_ids:
        print("No mailboxes available.")
        return []

    while True:
        selected_mailboxes = q.checkbox(
            "Select mailbox(es)", choices=[mailbox for mailbox in mailbox_ids.keys()]
        ).ask()

        if len(selected_mailboxes) != 0:
            break

        print("Please select at least one mailbox")

    selected_mailbox_ids = []
    for box in selected_mailboxes:
        selected_mailbox_ids.append(mailbox_ids[box])
    return selected_mailbox_ids


def list_mailboxes(config):
    """List all mailboxes"""
    mailboxes = get_mailboxes(config)
    if not mailboxes:
        return

    table_data = []
    for mailbox in mailboxes:
        default_status = "✓" if mailbox.get('default', False) else ""
        table_data.append([
            mailbox['id'],
            mailbox['email'],
            default_status,
            format_datetime(mailbox.get('creation_date', 'N/A'))
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
            if args['custom']:
                prefix = args['<prefix>']
                if args['--mailboxes']:
                    mailbox_ids = [int(id.strip()) for id in args['--mailboxes'].split(',')]
                else:
                    mailbox_ids = select_mailboxes(config)
                create_custom_alias(
                    config,
                    prefix,
                    mailbox_ids=mailbox_ids,
                    note=args['--note'],
                    name=args['--name']
                )
            elif args['random']:
                create_random_alias(
                    config,
                    mode=args['--mode'],
                    note=args['--note']
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

    elif args['contacts']:
        if args['list']:
            list_contacts(config, args['<alias_id>'])
            return
        elif args['create']:
            create_contact(config, args['<alias_id>'], args['<contact>'])
            return
        elif args['delete']:
            delete_contact(config, args['<contact_id>'])
            return
        elif args['toggle']:
            toggle_contact(config, args['<contact_id>'])
            return

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

    elif args['mailboxes'] and args['list']:
        list_mailboxes(config)
        return

    print("Command not recognized. Use --help to see available commands.")


if __name__ == "__main__":
    main()