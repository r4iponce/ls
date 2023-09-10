"""Admin view, manager url redirection."""

import re

import validators
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug import Response

from ls import get_config_dict
from ls.db import get_db

admin = Blueprint("admin", __name__)

SHORTENER_DOMAIN = get_config_dict()["shortener_domain"]


def verify_link_exist(url: str) -> bool:
    """
    Verify if a url already exist in database
    :param url: redirect source url
    :return: Bool, true if existed, else false.
    """
    db = get_db()
    query = db.execute("SELECT EXISTS(SELECT * FROM link  WHERE url=?)", (url,))
    result = query.fetchall()
    return result[0][0] == 1


@admin.route("/", host=SHORTENER_DOMAIN)
@login_required
def create() -> str:
    """
    Shorten link create page
    :return: the html template.
    """
    return render_template("create_link.html")


@admin.route("/", methods=["POST"], host=SHORTENER_DOMAIN)
@login_required
def create_post() -> Response | tuple[str, int]:
    """
    Processes user form and insert data in DB
    :return: A tuple[str, int] with return message and http code.
    """
    db = get_db()
    shortened_url = request.form["shortened_url"]
    real_url = request.form["real_url"]
    if not verify_link_exist(shortened_url):
        valid_regex = re.compile("[a-zA-Z0-9-_]+")
        if valid_regex.match(shortened_url) and validators.url(real_url):
            db.execute(
                "INSERT INTO link (url, real_url) VALUES (?, ?)",
                (shortened_url, real_url),
            ),
            db.commit()
            flash(
                f"https://{SHORTENER_DOMAIN}/{shortened_url} redirect to {real_url}",
                "success",
            )
            return redirect(url_for("admin.create_post"))
        flash(
            "Incorrect value",
            "error",
        )
        return render_template("create_link.html"), 400
    flash(
        "Link already exist",
        "error",
    )
    return render_template("create_link.html"), 400
