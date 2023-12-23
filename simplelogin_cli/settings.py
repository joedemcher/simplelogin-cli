import requests
import keyring
import os
import logging
from rich import print
from rich.logging import RichHandler

API_URL = os.environ.get("SIMPLELOGIN_API_URL")
ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")

log = logging.getLogger("rich")


def get_alias_generation_mode():
    headers = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}

    response = requests.get(url=f"{API_URL}/api/setting", headers=headers)

    data = response.json()
    return data["alias_generator"]
