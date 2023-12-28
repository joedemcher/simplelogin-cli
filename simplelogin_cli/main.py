#!/usr/bin/env python3

import os
import click
import auth
import alias as aleeas
import keyring
import logging
import settings
import questionary as q
import validators
from validators import ValidationError
from rich import print
from rich.logging import RichHandler

# Format logger
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
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

    auth.login(email, password, device_name)

    print("User has been logged in")


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


# TODO check that user is logged in
@cli.command(help="Get user's stats")
def stats():
    if not pre_check():
        exit(1)

    stats = settings.get_user_stats()
    print(stats)


# TODO check that user is logged in
@cli.command(help="Generate an alias")
@click.option("--prefix", help="The user generated prefix for the alias")
# @click.option(
#     "-m",
#     "--mailbox",
#     help="The email address that will own this alias",
# )
@click.option("--note", help="Add a note to the alias")
@click.option("--name", help="Name the alias")
def create(prefix, note, name):
    if not prefix:
        prefix = q.text("Alias prefix:").ask()

    mailboxes = aleeas.get_mailboxes()

    if len(mailboxes) == 0:
        print("No mailboxes found")
        exit(0)

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

    suffixes = aleeas.get_suffixes()

    suffix = q.select(
        "Select your email suffix",
        choices=[key for key in suffixes.keys()],
    ).ask()

    custom_alias = aleeas.generate_custom_alias(prefix, note, name, suffix, mailbox_ids)
    print(custom_alias)


# TODO Deal with nonexistence of env vars
def check_for_env_vars():
    if "SIMPLELOGIN_API_URL" in os.environ.keys():
        api_url = os.environ.get("SIMPLELOGIN_API_URL")
        valid_url = validators.url(api_url.strip())

        if isinstance(valid_url, ValidationError):
            return False

    if "SIMPLELOGIN_EMAIL" in os.environ.keys():
        email = os.environ.get("SIMPLELOGIN_EMAIL")
        valid_email = validators.email(email)

        if isinstance(valid_email, ValidationError):
            return False

    return True


def check_for_password():
    password = keyring.get_password("Simplelogin", ACCT_EMAIL)
    return False if password is None else True


def pre_check():
    if not check_for_env_vars():
        print("Environmental variables are not correctly set")
        return False

    if not check_for_password():
        print("You are not logged in, try 'sl login'")
        return False

    return True


if __name__ == "__main__":
    cli()
