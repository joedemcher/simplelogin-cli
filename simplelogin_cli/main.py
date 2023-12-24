#!/usr/bin/env python3

import click
import auth
import alias as al
import keyring
import logging
import settings
import questionary as q
from rich import print
from rich.logging import RichHandler

# Format logger
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


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


# TODO check that user is logged in
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
    print(al.list_aliases(filter_flag))


cli.add_command(alias)


# TODO check that user is logged in
@cli.command(help="Generate a random alias")
@click.option("--note", help="Add a note to the alias")
# TODO Hostname option
def random(note):
    mode = settings.get_alias_generation_mode()
    print(al.generate_random_alias(mode, note))


cli.add_command(random)


# TODO check that user is logged in
@cli.command(help="Get user's stats")
def stats():
    print(settings.get_user_stats())


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
    mailboxes = al.get_mailboxes()
    if len(mailboxes) == 0:
        print("No mailboxes found")
        return
    selected_mailboxes = q.checkbox(
        "Select mailbox", choices=[mailbox for mailbox in mailboxes.keys()]
    ).ask()
    mailbox_ids = []
    for box in selected_mailboxes:
        mailbox_ids.append(mailboxes[box])
    suffixes = al.get_suffixes()
    suffix = q.select(
        "Select your email suffix",
        choices=[key for key in suffixes.keys()],
    ).ask()

    print(al.generate_custom_alias(prefix, note, name, suffix, mailbox_ids))


if __name__ == "__main__":
    cli()
