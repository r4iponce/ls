"""Admin view, manager url redirection."""

import re

import validators
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug import Response

from ls.config import get_admin_domain, get_shortener_domain
from ls.db import get_db
from ls.utils import verify_link_exist

admin = Blueprint("admin", __name__)

ADMIN_DOMAIN = get_admin_domain()
SHORTENER_DOMAIN = get_shortener_domain()


@admin.route("/", host=ADMIN_DOMAIN)
@login_required
def create() -> str:
    """
    Shorten link create page
    :return: the html template.
    """
    return render_template("create_link.html.j2")


@admin.route("/", methods=["POST"], host=ADMIN_DOMAIN)
@login_required
def create_post() -> Response | tuple[str, int]:
    """
    Processes user form and insert data in DB
    :return: A tuple[str, int] with return message and http code.
    """
    db = get_db()
    shortened_url = request.form["shortened_url"]
    real_url = request.form["real_url"]
    if len(shortened_url) <= 10 and len(real_url) <= 100:
        if not verify_link_exist(shortened_url):
            valid_regex = re.compile("[a-zA-Z0-9-_]+")
            if valid_regex.match(shortened_url) and validators.url(real_url):
                db.execute(
                    "INSERT INTO link (url, real_url, owner) VALUES (?, ?, ?)",
                    (shortened_url, real_url, current_user.get_id()),
                ),
                db.commit()
                flash(
                    f"https://{SHORTENER_DOMAIN}/{shortened_url} redirect to {real_url}",  # noqa: E501
                    "success",
                )
                return redirect(url_for("admin.create_post"))
            flash(
                "Incorrect value",
                "error",
            )
            return render_template("create_link.html.j2"), 400
        flash(
            "Link already exist",
            "error",
        )
        return render_template("create_link.html.j2"), 400
    flash("Source url or Redirect to are to long (max 10 and max 100 characters)")
    return render_template("create_link.html.j2"), 400
