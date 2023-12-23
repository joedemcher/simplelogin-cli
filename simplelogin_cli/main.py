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


@cli.command(help="Login to Simplelogin")
def login():
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")
    device_name = "SL CLI"
    auth.login(email, password, device_name)
    print("Logged in successfully.")


cli.add_command(login)


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
    print(aliases.list_aliases(filter_flag))


cli.add_command(alias)


@cli.command(help="Generate a random alias")
# @click.option("-u", "--uuid")
# @click.option("-w", "--word", is_flag=True)
def random():
    aliases.generate_random_alias()


cli.add_command(random)

if __name__ == "__main__":
    cli()
