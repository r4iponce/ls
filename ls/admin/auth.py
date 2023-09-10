"""Manager user authentification."""

import random
import string
from getpass import getpass

import click
import werkzeug.security
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from werkzeug import Response

from ls import get_config_dict
from ls.admin.user import load_user
from ls.db import get_db

auth = Blueprint(
    "auth",
    __name__,
)


SHORTENER_DOMAIN = get_config_dict()["shortener_domain"]


def verify_user_exist(name: str) -> bool:
    """
    Verify if user exist in database
    :param name: name of user
    :return: bool, true if user existed, else false.
    """
    db = get_db()
    query = db.execute("SELECT EXISTS(SELECT * FROM user  WHERE name=?)", (name,))
    result = query.fetchall()
    return result[0][0] == 1  # first [0] row, second column


def validate_login(name: str, password: str) -> bool:
    """
    Validate if login information are correct
    :param name: name of user to verify
    :param password: password to verify if match with user
    :return: True if password AND user match, else False.
    """
    db = get_db()
    if verify_user_exist(name):
        query = db.execute("SELECT password FROM user  WHERE name=?", (name,))
        hashed_password = query.fetchall()[0][0]
        if werkzeug.security.check_password_hash(hashed_password, password):
            return True
        return False
    werkzeug.security.generate_password_hash(
        "".join(random.choice(string.ascii_letters) for _ in range(16))  # noqa: S311
    )  # Prevent user guess based on response time
    return False


@auth.route("/login", host=SHORTENER_DOMAIN)
def login() -> str:
    """
    Login page
    :return: login page template.
    """
    return render_template("login.html")


@auth.route("/login", host=SHORTENER_DOMAIN, methods=["POST"])
def login_post() -> Response:
    """
    Process login page form
    :return: redirect to create link if correct auth, else return to login page.
    """
    db = get_db()
    user = request.form.get("user")
    password = request.form.get("password")
    remember = bool(request.form.get("remember"))
    curs = db.cursor()
    if validate_login(user, password):
        curs.execute("SELECT * FROM user WHERE name=?", [user])
        user_data_list = list(curs.fetchone())
        user_data = load_user(user_data_list[0])
        login_user(user_data, remember=remember)
        return redirect(url_for("admin.create"))
    flash("Bad user or password, please retry")
    return redirect(url_for("auth.login"))


@auth.route("/logout", host=SHORTENER_DOMAIN)
def logout() -> Response:
    """
    Logout user
    :return: redirect to login page.
    """
    logout_user()
    return redirect(url_for("auth.login"))


def create_user(user: str, password: str) -> None:
    """
    Create a user
    :param user: username
    :param password: password of user
    :return: None.
    """
    hashed_password = werkzeug.security.generate_password_hash(
        password, method="scrypt"
    )
    db = get_db()
    db.execute(
        "INSERT INTO user(name, password) VALUES (?, ?)", (user, hashed_password)
    )
    db.commit()
    print("User created")  # noqa: T201


@auth.cli.command("create-user")
@click.argument("user")
def create_user_command(user: str) -> None:
    """
    Cli command for create user
    :param user: username of new user
    :return: None.
    """
    if not verify_user_exist(user):
        password = getpass("Enter user password here : ")
        create_user(user, password)
        click.echo(f"User {user} created")
    else:
        print("User already exist")  # noqa: T201
