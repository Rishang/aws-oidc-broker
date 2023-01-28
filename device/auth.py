# ref:
import time
import webbrowser

import typer
import requests

from utils import pprint

ALGORITHMS = ["RS256"]

# New code 👇
def login(domain: str, client_id: str, audience: str = None):
    """
    Runs the device authorization flow and stores the user object in memory
    """
    device_code_payload = {
        "client_id": client_id,
        "scope": "openid email profile",
        "audience": audience,
    }

    well_known = requests.get(
        f"https://{domain}/.well-known/openid-configuration"
    ).json()

    device_code_response = requests.post(
        well_known["device_authorization_endpoint"],
        data=device_code_payload,
    )

    if device_code_response.status_code != 200:
        print("Error generating the device code")
        raise typer.Exit(code=1)

    pprint("Device code successful")
    device_code_data = device_code_response.json()

    pprint(
        "1. On your computer or mobile device navigate to: ",
        device_code_data["verification_uri_complete"],
    )
    pprint("2. Enter the following code: ", device_code_data["user_code"])

    webbrowser.open_new(device_code_data["verification_uri_complete"])

    token_payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code_data["device_code"],
        "client_id": client_id,
    }

    authenticated = False
    while not authenticated:
        pprint("- Checking if the user completed the flow...")
        token_response = requests.post(
            well_known["token_endpoint"],
            data=token_payload,
        )

        token_data = token_response.json()
        if token_response.status_code == 200:
            pprint("Authenticated!")
            authenticated = True
        elif token_data["error"] not in ("authorization_pending", "slow_down"):
            pprint(token_data["error_description"])
            raise typer.Exit(code=1)
        else:
            time.sleep(device_code_data["interval"])

    return token_data
