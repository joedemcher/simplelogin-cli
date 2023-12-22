#!/usr/bin/env python3
import requests
import keyring
import os
import logging
from rich import print
from rich.logging import RichHandler

API_URL = os.environ.get("SIMPLELOGIN_API_URL")
ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")

# Format logger
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


def get_aliases(pinned):
    # print(f"{pinned}, {enabled}, {disabled}, {query}")
    header = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}
    params = get_params(pinned)
    aliases = []
    page_id = 0
    pages = 0
    while True:
        response = requests.get(
            url=f"{API_URL}/api/v2/aliases", params=params, headers=header
        )
        # print(response.text)
        data = response.json()
        if data.get("aliases") is not None and pages < 1:
            for alias in data.get("aliases"):
                aliases.append(alias)
        else:
            break

        page_id += 1
        pages += 1
        params["page_id"] = page_id
    return "No aliases found" if len(aliases) == 0 else aliases


def get_params(pinned):
    params = {"page_id": 0}
    if pinned:
        params["pinned"] = "true"
    return params
