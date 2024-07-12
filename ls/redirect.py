"""Shortener itself."""

from flask import Blueprint, redirect, render_template
from werkzeug import Response

from ls.config.config import get_root_redirect, get_shortener_domain
from ls.db.db import get_link, verify_link_exist

redirect_url = Blueprint("redirect", __name__)


@redirect_url.route("/<path:path>", host=get_shortener_domain())
def make_redirect(path: str) -> Response | tuple[str, int]:
    """

    :param path: The fetched path
    :return: The redirection
    """
    if verify_link_exist(path):
        return redirect(get_link(path))

    return render_template("404.html.j2"), 404


@redirect_url.route("/", host=get_shortener_domain())
def root_redirect() -> Response:
    """:return: Redirect to defined url"""
    return redirect(get_root_redirect())
