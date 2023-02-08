# ref:
import os
import sys
import time
import webbrowser
import configparser
from typing import Optional

import typer
import requests

sys.path.append("../")

from device.utils import pprint, prompt, log
from device.config import AWS_CONFIG_FILE
from broker.aws import sts

ALGORITHMS = ["RS256"]


# New code 👇
def login(domain: str, client_id: str, audience: Optional[str] = ""):
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
        typer.echo("Error generating the device code")
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


def aws_console(profile: str):
    _profile = f"profile {profile}"
    config = configparser.ConfigParser()
    config.read(AWS_CONFIG_FILE)

    if not config.has_section(_profile):
        print(config.sections())
        raise typer.Exit(code=1)

    web_identity_token_file = config.get(_profile, "web_identity_token_file")
    role_arn = config.get(_profile, "role_arn")

    # extras
    region = config[_profile].get("region", "us-east-1")

    if os.path.exists(web_identity_token_file):
        with open(web_identity_token_file, "r") as t:
            token = t.read()
    else:
        log.error(f"token file: {web_identity_token_file} Not found", exit=True)

    console_access = sts.get_role(token=token, role=role_arn, region=region)["console"]

    yn = prompt.ask(
        f"\nProfile: {profile} | Region: {region}\nDo you want to open browser aws console - (Yes/no)"
    )

    if yn.lower() == "yes":
        webbrowser.open_new(console_access)
