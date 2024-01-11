#!/usr/bin/env python3

import requests
import keyring
import os
import logging
from rich import print


# TODO remove this maybe to an API class?
API_URL = os.environ.get("SIMPLELOGIN_API_URL")
ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")
API_KEY = keyring.get_password("Simplelogin", ACCT_EMAIL)

log = logging.getLogger("rich")


def list_aliases(filter_flag):
    headers = {"Authentication": API_KEY}
    params = get_params(filter_flag)
    aliases = {"aliases": []}
    page_id = 0
    # if query:
    #     payload = {"query": query}
    # else:
    #     payload = {}

    while True:
        try:
            response = requests.get(
                url=f"{API_URL}/api/v2/aliases", params=params, headers=headers
            )

            response.raise_for_status()

            data = response.json()

            if len(data.get("aliases")) != 0:
                aliases["aliases"] = aliases.get("aliases") + data.get("aliases")
            else:
                break

        except requests.exceptions.RequestException as e:
            log.error(f"Request error: {e}")
            print("Error fetching all aliases")
            exit(1)

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
        "Authentication": API_KEY,
        "Content-Type": "application/json",
    }
    params = {"mode": mode}
    payload = {"note": note} if note else {}
    url = f"{API_URL}/api/alias/random/new"

    try:
        response = requests.post(url, headers=headers, json=payload, params=params)

        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")

    return "Alias could not be created."


# Keep getting 412 error because it's taking too long to create an alias¿
def generate_custom_alias(prefix, note, name, suffix, mailbox_ids):
    headers = {
        "Authentication": API_KEY,
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
        log.error(f"Request error: {e}")

    return "Alias could not be created."


# TODO Check that user is able to make new alias
def get_suffixes():
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/v5/alias/options"

    try:
        response = requests.get(url, headers=headers)

        response.raise_for_status()

        data = response.json()

        suffixes = {}

        for suffix in data["suffixes"]:
            suffixes[suffix["suffix"]] = suffix["signed_suffix"]

        return suffixes
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Could not fetch suffixes")
        exit(1)


def get_mailboxes():
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/v2/mailboxes"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        mailboxes = {}

        for mailbox in data["mailboxes"]:
            mailboxes[mailbox["email"]] = mailbox["id"]

        return mailboxes
    except requests.exceptions.RequestException as e:
        log.error(f"Request error {e}")
        print("Could not fetch mailboxes")
        exit(1)


def delete_alias(alias_id):
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/aliases/{alias_id}"

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        print("Alias deleted")
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Could not delete alias")
        exit(1)


def get_alias(alias_id):
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/aliases/{alias_id}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Could not get alias to confirm")
        exit(1)


def toggle_alias(alias_id):
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/aliases/{alias_id}/toggle"

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Could not toggle alias")
        exit(1)
