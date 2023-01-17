"""
Main routes file for running server, to start server 
run: python routes.py 
"""

import os
import json

from flask import request, session, url_for, redirect, jsonify, render_template

from aws import sts
from serve import app, keycloak_oidc, title
from utils import msg

# flask cors import
# from flask_cors import CORS


@app.route("/home")
@app.route("/")
def homepage():
    """application homepage"""

    userinfo = session.get("user")
    if userinfo:
        return render_template("index.html", title=title, userinfo=json.dumps(userinfo))
    else:
        return render_template("index.html", title=title, userinfo=json.dumps({}))


@app.route("/login", methods=["GET"])
def login():
    """login client path"""

    args: dict = request.args.to_dict()

    if session.get("user"):
        return redirect(url_for("homepage"))

    redirect_uri = url_for("auth", _external=True, role=args.get("role"), type="cli")
    return keycloak_oidc.authorize_redirect(redirect_uri)


@app.route("/userinfo")
def userinfo():
    """userinfo of authenticated user provided via oidc provider"""

    userinfo = session.get("user")
    return jsonify(userinfo)


@app.route("/logout")
def logout():
    """logout and remove user session"""

    session.clear()
    return redirect(url_for("homepage"))


@app.route("/auth")
def auth():
    """authenticate user via oidc provider"""

    token = keycloak_oidc.authorize_access_token()

    if "userinfo" in token:
        session["user"] = token["userinfo"]
    else:
        user = keycloak_oidc.userinfo(token=token)
        session["user"] = user

    args: dict = request.args.to_dict()

    if session.get("user") and args.get("role") != None:
        return redirect(url_for("aws_auth", role=args.get("role"), type="cli"))

    return redirect(url_for("homepage"))


@app.route("/aws", methods=["GET"])
def aws_auth():
    """provide aws iam role based creds to"""

    args: dict = request.args.to_dict()

    role: str = args.get("role")
    region: str = args.get("region")
    userinfo = session.get("user")
    type: str = args.get("type")
    duration_s: str = args.get("duration_seconds") or 3600

    if None in [userinfo, role]:
        return redirect(url_for("login", role=role))

    if role not in userinfo.get("roles"):
        return jsonify(msg.error("Invalid Role"))

    redirect_uri = url_for("auth", _external=True)
    token = keycloak_oidc.fetch_access_token(redirect_uri)

    sts_role = sts.get_role(
        token=token["access_token"],
        role=role,
        username=userinfo.get("preferred_username"),
        issuer=request.headers.get("Host"),
        region=region,
        duration_seconds=int(duration_s),
    )

    if sts_role["expired"] == True:
        return redirect(url_for("login"))

    if type == "cli":
        return jsonify(sts_role["cli"])
    elif type == "console":
        return redirect(sts_role["console"])


if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV")
    if isinstance(env, str) and env.lower() in ["main", "master"]:
        app.run()
    else:
        app.run(debug=True)
