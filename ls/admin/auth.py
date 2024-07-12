"""Manage user authentication."""

import random
import string

import werkzeug.security
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug import Response

from ls.config.config import get_admin_domain
from ls.db.db import get_db, get_user

auth = Blueprint(
    "auth",
    __name__,
)


def verify_user_exist(name: str) -> bool:
    """
    Verify if user exist in database
    :param name: name of user
    :return: bool, true if user existed, else false.
    """
    db = get_db()
    query = db.execute(
        "SELECT EXISTS(SELECT * FROM user  WHERE name=?)", (name.lower(),)
    )
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
        query = db.execute("SELECT password FROM user  WHERE name=?", (name.lower(),))
        hashed_password = query.fetchall()[0][0]
        if werkzeug.security.check_password_hash(hashed_password, password):
            return True
    werkzeug.security.generate_password_hash(
        "".join(random.choice(string.ascii_letters) for _ in range(16))  # noqa: S311
    )  # Prevent user guess based on response time
    return False


@auth.route("/login", host=get_admin_domain())
def login() -> str:
    """
    Login page
    :return: login page template.
    """
    return render_template("login.html.j2")


@auth.route("/login", host=get_admin_domain(), methods=["POST"])
def login_post() -> Response:
    """
    Process login page form
    :return: redirect to create link if correct auth, else return to login page.
    """
    db = get_db()
    user = request.form.get("user")
    if user == "" or user is None:
        flash("User cannot be empty", "error")
        return redirect(url_for("auth.login"))

    user = user.lower()
    password = request.form.get("password")

    if password == "" or password is None:
        flash("Password cannot be empty", "error")
        return redirect(url_for("auth.login"))

    remember = bool(request.form.get("remember"))
    curs = db.cursor()
    max_user_length = 100
    if len(user) < max_user_length and len(password) < max_user_length:
        if validate_login(user, password):
            curs.execute("SELECT * FROM user WHERE name=?", [user])
            user_data_list = list(curs.fetchone())
            user_data = get_user(user_data_list[0])
            login_user(user_data, remember=remember)
            flash(
                f"Welcome {current_user.get_name()}",
                "success",
            )
            return redirect(url_for("admin.create"))
        flash("Bad user or password, please retry", "error")
        return redirect(url_for("auth.login"))
    flash("Password or user too long, max 100 characters", "error")
    return redirect(url_for("auth.login"))


@auth.route("/logout", host=())
def logout() -> Response:
    """
    Logout user
    :return: redirect to login page.
    """
    logout_user()
    return redirect(url_for("auth.login"))
