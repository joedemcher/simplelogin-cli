#!/usr/bin/env python3

import requests
import getpass
import keyring
import os

API_URL = os.environ.get("SIMPLELOGIN_API_URL")


def login(email, password, device):
    payload = {"email": email, "password": password, "device": device}

    response = requests.post(f"{API_URL}/api/auth/login", json=payload)

    if response.status_code == 200:
        data = response.json()

        if data.get("mfa_enabled"):
            mfa_token = getpass.getpass("Enter your OTP: ")
            mfa(email, mfa_token, data.get("mfa_key"), device)
        else:
            keyring.set_password("Simplelogin", email, data.get("api_key"))
            return
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def mfa(email, mfa_token, mfa_key, device_name):
    payload = {"mfa_token": mfa_token, "mfa_key": mfa_key, "device": device_name}
    response = requests.post(f"{API_URL}/api/auth/mfa", json=payload)
    if response.status_code == 200:
        data = response.json()
        keyring.set_password("Simplelogin", email, data.get("api_key"))
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
