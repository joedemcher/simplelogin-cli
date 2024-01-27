#!/usr/bin/env python3

import os
import click
import keyring
import logging
import questionary as q
import validators

from validators import ValidationError
from rich import print
from rich.logging import RichHandler

import alias as aleeas
import settings

# Format logger
FORMAT = "%(message)s"
logging.basicConfig(
    level="WARN",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])],
)

log = logging.getLogger("rich")

ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")


@click.group()
def cli():
    pass


@cli.command(help="Login to Simplelogin")
@click.option("--email", help="The email used to login to Simplelogin")
def login(email):
    if not email:
        email = q.text("Enter your email:").ask()

    password = q.password("Enter your password:").ask()
    device_name = "SL CLI"

    settings.login(email, password, device_name)

    print("User has been logged in")


@cli.command(help="Logout of Simplelogin")
def logout():
    if not pre_check():
        exit(1)

    if settings.logout(ACCT_EMAIL):
        print("User has been logged out")

    # print("User has not been logged out")


@cli.command(help="List your aliases")
@click.option(
    "--all",
    "filter_flag",
    flag_value="all",
    default=True,
    show_default=True,
    help="All aliases are returned",
)
@click.option(
    "-p",
    "--pinned",
    "filter_flag",
    flag_value="pinned",
    help="Only pinned aliases are returned",
)
@click.option(
    "-e",
    "--enabled",
    "filter_flag",
    flag_value="enabled",
    help="Only enabled aliases are returned",
)
@click.option(
    "-d",
    "--disabled",
    "filter_flag",
    flag_value="disabled",
    help="Only disabled aliases are returned",
)
# TODO Add query option
# @click.option(
#     "-q",
#     "--query",
#     default="",
#     required=False,
#     help="The query that will be used for search",
# )
def alias(filter_flag):
    if not pre_check():
        exit(1)

    aliases = aleeas.list_aliases(filter_flag)
    print(aliases)


@cli.command(help="Generate a random alias")
@click.option("--note", help="Add a note to the alias")
# TODO Hostname option
def random(note):
    if not pre_check():
        exit(1)

    mode = settings.get_alias_generation_mode()
    random_alias = aleeas.generate_random_alias(mode, note)
    print(random_alias)


@cli.command(help="Delete an alias")
@click.option("-a", help="The alias id of the alias that will be deleted")
def delete(a):
    if not pre_check():
        exit(1)

    if not a:
        a = q.text("Alias ID:").ask()

    confirm_alias = aleeas.get_alias(a)
    print(confirm_alias)
    confirm = q.confirm("Are you sure you want to delete the above alias?", False).ask()
    if confirm:
        aleeas.delete_alias(a)


@cli.command(help="Get user's stats")
def stats():
    if not pre_check():
        exit(1)

    stats = settings.get_user_stats()
    print(stats)


# TODO check that user is logged in
@cli.command(help="Generate an alias")
@click.option("-p", "--prefix", help="The user generated prefix for the alias")
# @click.option(
#     "-m",
#     "--mailbox",
#     help="The email address that will own this alias",
# )
@click.option("--note", help="Add a note to the alias")
@click.option("--name", help="Name the alias")
def create(prefix, note, name):
    if not pre_check():
        exit(1)

    if not prefix:
        prefix = q.text("Alias prefix:").ask()

    mailboxes = aleeas.get_mailboxes()

    if len(mailboxes) == 0:
        print("No mailboxes found")
        exit(0)

    mailbox_ids = select_mailboxes(mailboxes)

    suffixes = aleeas.get_suffixes()

    suffix_key = q.select(
        "Select your email suffix",
        choices=[key for key in suffixes.keys()],
    ).ask()

    custom_alias = aleeas.generate_custom_alias(
        prefix, note, name, suffixes.get(suffix_key), mailbox_ids
    )

    print(custom_alias)


@cli.command(help="Toggle an alias on/off")
@click.option("-a", help="The alias ID that will be toggled")
def toggle(a):
    if not pre_check():
        exit(1)

    if not a:
        a = q.text("Alias ID:").ask()

    toggled = aleeas.toggle_alias(a)
    print("Alias enabled") if toggled.get("enabled") else print("Alias disabled")


def select_mailboxes(mailboxes):
    """
    Prompts the user to choose their mailbox(es) for alias generation.
    """
    while True:
        selected_mailboxes = q.checkbox(
            "Select mailbox(es)", choices=[mailbox for mailbox in mailboxes.keys()]
        ).ask()

        if len(selected_mailboxes) != 0:
            break

        print("Please select at least one mailbox")

    mailbox_ids = []

    for box in selected_mailboxes:
        mailbox_ids.append(mailboxes[box])

    return mailbox_ids


def check_for_env_vars():
    """
    Confirms the  necessary environmental variables are set correctly.
    """
    if (
        "SIMPLELOGIN_API_URL" in os.environ.keys()
        and "SIMPLELOGIN_EMAIL" in os.environ.keys()
    ):
        api_url = os.environ.get("SIMPLELOGIN_API_URL")
        valid_url = validators.url(api_url.strip())
        email = os.environ.get("SIMPLELOGIN_EMAIL")
        valid_email = validators.email(email)

        return (
            False
            if isinstance(valid_url, ValidationError)
            or isinstance(valid_email, ValidationError)
            else True
        )
    return False


def check_for_password():
    """
    Confirm the API key is stored in system keyring.
    """
    password = keyring.get_password("Simplelogin", ACCT_EMAIL)
    return False if password is None else True


def pre_check():
    """
    Checks for the necessary set up by the user.
    """
    if not check_for_env_vars():
        print("Environmental variables are not correctly set")
        return False

    if not check_for_password():
        print("You are not logged in, try 'simplelogin login'")
        return False

    return True


if __name__ == "__main__":
    cli()
