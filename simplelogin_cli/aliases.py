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


def get_aliases(filter_flag):
    header = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}
    params = get_params(filter_flag)
    aliases = {"aliases": []}
    page_id = 0
    # if query:
    #     payload = {"query": query}
    # else:
    #     payload = {}
    while True:
        # TODO catch errors
        response = requests.get(
            url=f"{API_URL}/api/v2/aliases", params=params, headers=header
        )
        if response.status_code == 200:
            data = response.json()
            if len(data.get("aliases")) != 0:
                aliases["aliases"] = aliases.get("aliases") + data.get("aliases")
            else:
                break
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

        page_id += 1
        params["page_id"] = page_id

    return "No aliases found." if len(aliases) == 0 else aliases


def get_params(filter_flag):
    params = {"page_id": 0}
    match filter_flag:
        case "pinned":
            params["pinned"] = "true"
        case "disabled":
            params["disabled"] = "true"
        case "enabled":
            params["enabled"] = "true"
    return params


def new_random_alias():
    return
