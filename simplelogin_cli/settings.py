import requests
import keyring
import os
import logging
from rich import print

API_URL = os.environ.get("SIMPLELOGIN_API_URL")
ACCT_EMAIL = os.environ.get("SIMPLELOGIN_EMAIL")
API_KEY = keyring.get_password("Simplelogin", ACCT_EMAIL)

log = logging.getLogger("rich")


def get_alias_generation_mode():
    headers = {"Authentication": API_KEY}

    response = requests.get(url=f"{API_URL}/api/setting", headers=headers)

    data = response.json()
    return data["alias_generator"]


def get_user_stats():
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/stats"

    response = requests.get(url, headers=headers)

    data = response.json()
    stats = {}
    for key, val in data.items():
        match key:
            case "nb_alias":
                stats["num_alias"] = val
            case "nb_block":
                stats["num_block"] = val
            case "nb_forward":
                stats["num_forward"] = val
            case "nb_reply":
                stats["num_reply"] = val
    return stats
