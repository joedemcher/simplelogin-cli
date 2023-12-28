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
    try:
        headers = {"Authentication": API_KEY}

        response = requests.get(url=f"{API_URL}/api/setting", headers=headers)

        data = response.json()

        return data["alias_generator"]
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Error fetching alias generation mode")
        exit(1)


def get_user_stats():
    headers = {"Authentication": API_KEY}
    url = f"{API_URL}/api/stats"

    try:
        response = requests.get(url, headers=headers)

        response.raise_for_status()

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
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Error fetching user's stats")
        exit(1)

    return stats
