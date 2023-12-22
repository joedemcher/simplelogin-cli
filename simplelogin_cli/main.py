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
    "-p",
    "--pinned",
    is_flag=True,
    show_default=True,
    default=False,
    help="Only pinned aliases are returned",
)
# @click.option(
#     "-d",
#     "--disabled",
#     is_flag=True,
#     # show_default=True,
#     default=False,
#     help="Only disabled aliases are returned",
# )
# @click.option(
#     "-e",
#     "--enabled",
#     is_flag=True,
#     # show_default=True,
#     default=False,
#     help="Only enabled aliases are returned",
# )
# @click.option(
#     "-q",
#     "--query",
#     default="",
#     required=False,
#     help="The query that will be used to search",
# )
def alias(pinned):
    print(aliases.get_aliases(pinned))


cli.add_command(alias)

if __name__ == "__main__":
    cli()
