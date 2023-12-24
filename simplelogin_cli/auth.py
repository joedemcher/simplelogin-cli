#!/usr/bin/env python3

import requests
import questionary as q
import keyring
import os

API_URL = os.environ.get("SIMPLELOGIN_API_URL")


def login(email, password, device):
    payload = {"email": email, "password": password, "device": device}

    response = requests.post(f"{API_URL}/api/auth/login", json=payload)

    if response.status_code == 200:
        data = response.json()

        if data.get("mfa_enabled"):
            mfa_token = q.password("Enter your OTP:").ask()
            api_key = mfa(email, mfa_token, data.get("mfa_key"), device)
        else:
            api_key = data.get("api_key")
        if api_key:
            keyring.set_password("Simplelogin", email, api_key)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def mfa(email, mfa_token, mfa_key, device_name):
    payload = {"mfa_token": mfa_token, "mfa_key": mfa_key, "device": device_name}
    response = requests.post(f"{API_URL}/api/auth/mfa", json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("api_key")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
