import os
from typing import Optional

import typer
import jwt

from device.auth import ALGORITHMS, aws_console, login as _login
from device.utils import HOME, md5hash, pprint, prompt
from device.config import (
    profiles,
    Profile,
    AwsConfig,
    awsconfig,
    _check_wellknown_openid,
    _check_aws_iam,
)

app = typer.Typer(help=f"AWS broker for different auth")


@app.command()
def config(
    profile: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="aws profile name to be created",
        prompt="AWS cli profile name",
    ),
    role: str = typer.Option(
        None,
        "--role",
        help="AWS IAM role arn which has to be accessed",
        prompt="AWS IAM OpenID fedrated role arn",
        callback=_check_aws_iam,
    ),
    client_wellknown: str = typer.Option(
        None,
        "--client-wellknown",
        help="auth oidc provider .well-known/openid-configuration url domain.",
        prompt=f"OpenID auth provider client wellknown url",
        callback=_check_wellknown_openid,
    ),
    client_id: str = typer.Option(
        None,
        "--client-id",
        help="Auth identification value assigned to your application after registration.",
        prompt="OpenID auth provider client_id",
    ),
    audience: Optional[str] = typer.Option(
        None,
        "--audience",
        help="OPTIONAL: Audience value is either the application (Client ID) for an ID Token or the API that is being called (API Identifier) for an Access Token.",
    ),
):
    if audience == None:
        audience = prompt.ask(f"OPTIONAL: OpenID auth provider audience", default="")

    profiles.set(
        key=profile,
        value=Profile(
            role_arn=role,
            client_id=client_id,
            client_wellknown=client_wellknown,
            audience=audience,
        ),
    )
    profiles.save()


@app.command(name="login")
def login(
    profile: str = typer.Option(
        "--profile", help="auth via oidc provider for aws access"
    )
):
    if profile == None:
        print("Required aws profile name")
        return

    _p: Profile = profiles.get(profile)
    token_data = _login(
        domain=_p.client_wellknown, client_id=_p.client_id, audience=_p.audience
    )

    access_token = token_data["access_token"]
    pprint(
        "[yellow bold]access_token payload => ",
        jwt.decode(
            access_token,
            algorithms=ALGORITHMS,
            options={"verify_signature": False},
        ),
    )

    filename = md5hash(profile)
    filepath = f"{HOME}/.aws/cli/cache"

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    with open(f"{filepath}/{filename}", "w") as token_file:
        token_file.write(access_token)

    awsconfig(
        profile=profile,
        aws_config=AwsConfig(
            web_identity_token_file=f"{filepath}/{filename}", role_arn=_p.role_arn
        ),
    )


@app.command(name="console")
def console(
    profile: str = typer.Option(
        None, "--profile", help="auth via oidc provider for aws console access"
    )
):
    if profile == None:
        print("Required aws profile name")
        return

    aws_console(profile)


if __name__ == "__main__":
    app()
