from getpass import getpass

import click
import werkzeug.security
from flask import Blueprint, render_template, request, flash, url_for, redirect
import random
import string

from flask_login import login_user

from ls.admin.user import load_user
from ls.db import get_db

auth = Blueprint(
    "auth",
    __name__,
)


def verify_user_exist(name: str) -> bool:
    db = get_db()
    query = db.execute("SELECT EXISTS(SELECT * FROM user  WHERE name=?)", (name,))
    result = query.fetchall()
    if result[0][0] == 1:  # first [0] row, second column
        return True
    else:
        return False


def validate_login(name: str, password: str) -> bool:
    db = get_db()
    print(name)
    if verify_user_exist(name):
        query = db.execute("SELECT password FROM user  WHERE name=?", (name,))
        hashed_password = query.fetchall()[0][0]
        if werkzeug.security.check_password_hash(hashed_password, password):
            return True
        return False
    else:
        werkzeug.security.generate_password_hash(
            "".join(random.choice(string.ascii_letters) for _ in range(16))
        )  # Prevent user guess based on response time
        return False


@auth.route("/login", host="127.0.0.1")
def login():
    return render_template("login.html")


@auth.route("/login", host="127.0.0.1", methods=["POST"])
def login_post():
    db = get_db()
    user = request.form.get("user")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    curs = db.cursor()
    curs.execute("SELECT * FROM user WHERE name=?", [user])
    user_data_list = list(curs.fetchone())
    user_data = load_user(user_data_list[0])
    if validate_login(user, password):
        login_user(user_data, remember=remember)
        return redirect(url_for("admin.create"))
    flash("Bad user or password, please retry")
    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    return "Logout"


def create_user(user: str, password: str) -> None:
    hashed_password = werkzeug.security.generate_password_hash(
        password, method="scrypt"
    )
    db = get_db()
    db.execute(
        "INSERT INTO user(name, password) VALUES (?, ?)", (user, hashed_password)
    )
    db.commit()
    print("User created")


@auth.cli.command("create-user")
@click.argument("user")
def create_user_command(user):
    """Create a user, argument : user"""
    if not verify_user_exist(user):
        password = getpass("Enter user password here : ")
        create_user(user, password)
        click.echo(f"User {user} created")
    else:
        print("User already exist")
