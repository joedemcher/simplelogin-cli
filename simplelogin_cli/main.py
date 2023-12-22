import click
import auth
import aliases
import getpass
import keyring
import logging
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


@cli.command()
def login():
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")
    device_name = "SL CLI"
    auth.login(email, password, device_name)
    print("Logged in successfully.")


cli.add_command(login)


@cli.command(help="Search your aliases")
@click.option(
    "--all",
    "params",
    flag_value="all",
    default=True,
    help="All aliases are returned",
)
@click.option(
    "-p",
    "--pinned",
    "params",
    flag_value="pinned",
    help="Only pinned aliases are returned",
)
@click.option(
    "-e",
    "--enabled",
    "params",
    flag_value="enabled",
    help="Only enabled aliases are returned",
)
@click.option(
    "-d",
    "--disabled",
    "params",
    flag_value="disable",
    help="Only disabled aliases are returned",
)
@click.option(
    "-q",
    "--query",
    default="",
    required=False,
    help="The query that will be used for search",
)
def alias(params, query):
    aliases.get_aliases(params, query)


cli.add_command(alias)

if __name__ == "__main__":
    cli()
