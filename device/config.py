import re
import configparser
from dataclasses import dataclass
from typing import Optional, Dict

import requests
import typer

# local
from device.utils import HOME
from device.state import State

STATE_CONFIG_FILE = f"{HOME}/.aws/oidc-profiles.json"
AWS_CONFIG_FILE = f"{HOME}/.aws/config"


@dataclass
class Profile:
    role_arn: str
    client_wellknown: str
    client_id: str
    audience: Optional[str] = ""

    def _check_aws_iam(self, arn: str):
        if re.search(r"^(arn:aws:iam::)([0-9]{12}):role\/([a-zA-Z0-9\-]+)", arn):
            return arn
        else:
            raise typer.BadParameter("Invalid iam role arn.")

    def _check_wellknown_openid(self, url: str):
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


@dataclass
class AwsConfig:
    """ref: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html"""

    web_identity_token_file: str
    role_arn: str


profiles: Dict[str, Profile] = State(STATE_CONFIG_FILE, obj=Profile)  # type: ignore


def awsconfig(profile: str, aws_config: AwsConfig | None = None, remove: bool = False):
    profile = f"profile {profile}"

    config = configparser.ConfigParser()
    config.read(AWS_CONFIG_FILE)
    write_flag = False

    if remove == True:
        if config.has_section(profile):
            config.remove_section(profile)
            write_flag = True

    else:
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
