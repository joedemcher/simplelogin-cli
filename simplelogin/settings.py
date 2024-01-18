import questionary as q
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


def login(email, password, device):
    payload = {"email": email, "password": password, "device": device}

    try:
        response = requests.post(f"{API_URL}/api/auth/login", json=payload)

        response.raise_for_status()

        data = response.json()

        # TODO loop for correct mfa response maybe twice?
        if data.get("mfa_enabled"):
            mfa_token = q.password("Enter your OTP:").ask()
            api_key = mfa(email, mfa_token, data.get("mfa_key"), device)
        else:
            api_key = data.get("api_key")

        if api_key:
            keyring.set_password("Simplelogin", email, api_key)

    except requests.exceptions.RequestException as e:
        print("User login failed")
        log.error(f"Request error: {e}")
        exit(1)


def mfa(email, mfa_token, mfa_key, device_name):
    url = f"{API_URL}/api/auth/mfa"
    payload = {"mfa_token": mfa_token, "mfa_key": mfa_key, "device": device_name}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("api_key")
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("User login failed")
        exit(1)


def logout(ACCT_EMAIL):
    # if force:
    #     keyring.delete_password("Simplelogin", ACCT_EMAIL)

    url = f"{API_URL}/api/logout"
    API_KEY = keyring.get_password("Simplelogin", ACCT_EMAIL)
    headers = {"Authentication": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        keyring.delete_password("Simplelogin", ACCT_EMAIL)
    except requests.exceptions.RequestException as e:
        log.error(f"Request error: {e}")
        print("Error logging out")
        return False
    return True
