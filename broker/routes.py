from flask import request, session, url_for, redirect, jsonify, render_template
from .aws import sts
from . import app, keycloak_oidc, title
from .utils import msg
import json

# flask cors import
# from flask_cors import CORS


@app.route("/home")
@app.route("/")
def homepage():
    userinfo = session.get("user")
    if userinfo:
        return render_template("index.html", title=title, userinfo=json.dumps(userinfo))
    else:
        return render_template("index.html", title=title, userinfo=json.dumps({}))


@app.route("/login")
def login():
    redirect_uri = url_for("auth", _external=True)
    return keycloak_oidc.authorize_redirect(redirect_uri)


@app.route("/userinfo")
def userinfo():
    userinfo = session.get("user")
    return jsonify(userinfo)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("homepage"))


@app.route("/auth")
def auth():
    keycloak_oidc.authorize_access_token()
    user = keycloak_oidc.userinfo()
    if user:
        session["user"] = user

    return redirect(url_for("homepage"))


@app.route("/aws", methods=["GET"])
def aws_auth():
    args: dict = request.args.to_dict()
    role: str = args.get("role")
    userinfo = session.get("user")
    type: str = args.get("type")

    if None in [userinfo, role]:
        return jsonify(msg("error", "Missing userinfo or role"))

    if role not in userinfo.get("roles"):
        return jsonify(msg.error("Invalid Role"))

    redirect_uri = url_for("auth", _external=True)
    token = keycloak_oidc.fetch_access_token(redirect_uri)

    sts_role = sts.get_role(
        token=token["access_token"],
        role=role,
        username=userinfo.get("preferred_username"),
    )
    if sts_role["expired"] == True:
        return redirect(url_for("login"))

    if type == "cli":
        return jsonify(sts_role["cli"])
    elif type == "console":
        return redirect(sts_role["console"])
