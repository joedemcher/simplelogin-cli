#!/usr/bin/env python3
import requests
import keyring
import os
from rich import print

API_URL = os.environ.get("SIMPLELOGIN_API_URL")
ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")


def get_aliases():
    # print(f"{pinned}, {enabled}, {disabled}, {query}")
    header = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}
    page_id = 0
    aliases = []
    while True:
        params = {
            "page_id": page_id,
            #     "pinned": pinned,
            #     "enabled": enabled,
            #     "disabled": disabled,
        }
        # print(params)
        response = requests.get(
            url=f"{API_URL}/api/v2/aliases", params=params, headers=header
        )
        # print(response.text)
        data = response.json()
        data.get("aliases")
        if data.get("aliases") is not None:
            for alias in data.get("aliases"):
                aliases.append(alias)
        else:
            break

        page_id += 1
    return "No aliases found" if len(aliases) == 0 else aliases
