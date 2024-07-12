"""Admin view, manager url redirection."""

import re

import validators
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug import Response

from ls.config.config import get_admin_domain
from ls.db.db import get_db, verify_link_exist

admin = Blueprint("admin", __name__)


@admin.route("/", host=get_admin_domain())
@login_required
def create() -> str:
    """
    Shorten link create page
    :return: the html template.
    """
    return render_template("create_link.html.j2")


@admin.route("/", methods=["POST"], host=get_admin_domain)
@login_required
def create_post() -> Response | tuple[str, int]:
    """
    Processes user form and insert data in DB
    :return: A tuple[str, int] with return message and http code.
    """
    db = get_db()
    shortened_url = request.form["shortened_url"]
    real_url = request.form["real_url"]

    if len(shortened_url) > 10:
        flash("Redirect url to are to long (max 10 characters)")

    if len(real_url) > 100:
        flash("Source url are to long (max 1024 characters)")

    if verify_link_exist(shortened_url):
        flash(
            "Link already exist",
            "error",
        )
        return render_template("create_link.html.j2"), 400

    valid_regex = re.compile("[a-zA-Z0-9-_]+")
    if valid_regex.match(shortened_url) and validators.url(real_url):
        db.execute(
            "INSERT INTO link (url, real_url, owner) VALUES (?, ?, ?)",
            (shortened_url, real_url, current_user.get_id()),
        ),
        db.commit()
        flash(
            f"{request.base_url}{shortened_url} redirect to {real_url}",
            "success",
        )
        return redirect(url_for("admin.create_post"))

    flash(
        "Incorrect value",
        "error",
    )
    return render_template("create_link.html.j2"), 400
