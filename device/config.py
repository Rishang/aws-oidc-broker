import configparser
from dataclasses import dataclass
from typing import Optional
import re

import requests
import typer

from utils import State, HOME, Logger

STATE_CONFIG_FILE = f"{HOME}/.aws/oidc-profiles.json"
AWS_CONFIG_FILE = f"{HOME}/.aws/config"

logger = Logger()


@dataclass
class Profile:
    role_arn: str
    client_wellknown: str
    client_id: str
    audience: Optional[str] = ""


@dataclass
class AwsConfig:
    """ref: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html"""

    web_identity_token_file: str
    role_arn: str


profiles = State(STATE_CONFIG_FILE, obj=Profile)


def awsconfig(profile: str, aws_config: AwsConfig):
    profile = f"profile {profile}"

    config = configparser.ConfigParser()
    config.read(AWS_CONFIG_FILE)
    write_flag = False

    if not config.has_section(profile):
        config.add_section(profile)

    for arg in aws_config.__annotations__:
        if not config.has_option(profile, arg):
            config.set(profile, arg, aws_config.__dict__[arg])
            write_flag = True

        elif aws_config.__dict__[arg] != config[profile][arg]:
            config[profile][arg] = aws_config.__dict__[arg]
            write_flag = True

    if write_flag:
        with open(AWS_CONFIG_FILE, "w") as configfile:
            config.write(configfile)


def _check_aws_iam(arn: str):
    if re.search(r"^(arn:aws:iam::)([0-9]{12}):role\/([a-zA-Z0-9\-]+)", arn):
        return arn
    else:
        raise typer.BadParameter("Invalid iam role arn.")


def _check_wellknown_openid(url: str):
    domain = re.sub(r"(https?:\/\/)?(\.well-known.+)?", "", url)

    if domain[-1] == "/":
        domain = domain[:-1]

    try:
        requests.get(f"https://{domain}/.well-known/openid-configuration").json()
    except:
        raise typer.BadParameter(
            "Invalid openid-configuration domain.", param_hint="op"
        )

    return domain
