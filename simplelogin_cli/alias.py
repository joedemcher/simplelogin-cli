#!/usr/bin/env python3

import requests
import keyring
import os
import logging
from rich import print
from rich.logging import RichHandler

API_URL = os.environ.get("SIMPLELOGIN_API_URL")
ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")

log = logging.getLogger("rich")


def list_aliases(filter_flag):
    headers = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}
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
            url=f"{API_URL}/api/v2/aliases", params=params, headers=headers
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

    return "No aliases found." if len(aliases["aliases"]) == 0 else aliases


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


def generate_random_alias(mode, note):
    headers = {
        "Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL),
        "Content-Type": "application/json",
    }
    params = {"mode": mode}
    payload = {"note": note} if note else {}
    url = f"{API_URL}/api/alias/random/new"

    try:
        response = requests.post(url, headers=headers, json=payload)

        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    return "Alias could not be created."


def generate_custom_alias(prefix, note, name, suffix, mailbox_ids):
    headers = {
        "Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL),
        "Content-Type": "application/json",
    }

    url = f"{API_URL}/api/v3/alias/custom/new"
    payload = {
        "alias_prefix": prefix,
        "signed_suffix": suffix,
        "mailbox_ids": mailbox_ids,
    }

    if note:
        payload["note"] = note

    if name:
        payload["name"] = name

    try:
        response = requests.post(url, headers=headers, json=payload)

        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    return "Alias could not be created."


def get_suffixes():
    headers = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}
    url = f"{API_URL}/api/v5/alias/options"

    response = requests.get(url, headers=headers)
    data = response.json()

    suffixes = {}

    for suffix in data["suffixes"]:
        suffixes[suffix["suffix"]] = suffix["signed_suffix"]

    return suffixes


def get_mailboxes():
    headers = {"Authentication": keyring.get_password("Simplelogin", ACCT_EMAIL)}
    url = f"{API_URL}/api/v2/mailboxes"

    response = requests.get(url, headers=headers)
    data = response.json()

    mailboxes = {}

    for mailbox in data["mailboxes"]:
        mailboxes[mailbox["email"]] = mailbox["id"]

    return mailboxes
