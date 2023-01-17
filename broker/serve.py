"""
Flask oidc clinet for keycloak

ref: https://github.com/authlib/demo-oauth-client/tree/master/flask-google-login
"""
from flask import Flask
from authlib.integrations.flask_client import OAuth, FlaskOAuth2App

from data import KeyCloakOpenIdconfig
from utils import obj_annotations, load_or_read_env

app = Flask(
    __name__,
    static_url_path="",
    static_folder="web/static",
    template_folder="web/templates",
)

jinja_options = app.jinja_options.copy()
jinja_options.update(
    dict(
        variable_start_string="{:",
        variable_end_string=":}",
    )
)

app.jinja_options = jinja_options

PROVIDER = "keycloak"


def oidc_conf(provider: str, config_path: str = "../.env"):
    """Read oidc config from dotenv file"""

    if provider.lower() == "keycloak":
        _v = load_or_read_env(
            items=obj_annotations(KeyCloakOpenIdconfig), env_path=config_path
        )
        return KeyCloakOpenIdconfig(**_v)


config = oidc_conf(provider=PROVIDER)
app.config.from_object(config)

app.secret_key = (config.APP_SECRET == "" and "!somesecret") or config.APP_SECRET
title = (config.TITLE == "" and "Keycloak") or config.TITLE.capitalize()

oauth = OAuth(app)
oauth.register(
    name=PROVIDER,
    server_metadata_url=config.KEYCLOAK_WELLKNOWN,
    client_kwargs={"scope": "openid email profile"},
)

keycloak_oidc: FlaskOAuth2App = oauth.create_client(PROVIDER)
