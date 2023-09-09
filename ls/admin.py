from flask import Blueprint, render_template, redirect, url_for, request, current_app
from .db import get_db
import validators, re

admin = Blueprint("admin", __name__)


# @admin.route("/login")
# def login():
#     return render_template("login.html")
#
#
# @admin.route("/login", methods=["POST"])
# def login_post():
#     return redirect(url_for("create_link.create"))
#
#
# @admin.route("/logout")
# def logout():
#     return "Logout"


def verify_link_exist(url) -> bool:
    db = get_db()
    query = db.execute("SELECT EXISTS(SELECT * FROM link  WHERE url=?)", (url,))
    result = query.fetchall()
    if result[0][0] == 1:  # first [0] row, second column
        return True
    else:
        return False


@admin.route("/", host="localhost")
def create() -> str:
    return render_template("create_link.html")


@admin.route("/", methods=["POST"])
def create_post() -> str:
    db = get_db()
    shortened_url = request.form["shortened_url"]
    real_url = request.form["real_url"]
    print(verify_link_exist(shortened_url))
    if not verify_link_exist(shortened_url):
        valid_regex = re.compile("[a-zA-Z0-9-_]+")
        if valid_regex.match(shortened_url) and validators.url(real_url):
            db.execute(
                "INSERT INTO link (url, real_url) VALUES (?, ?)",
                (shortened_url, real_url),
            ),
            db.commit()
            return "success", 200
        else:
            return "Incorrect value", 400
    else:
        return "Link already exist", 400
