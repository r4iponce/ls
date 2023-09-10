"""Shortener itself."""

from flask import Blueprint, redirect, render_template
from werkzeug import Response

from ls.config import get_root_redirect, get_shortener_domain
from ls.db import get_db
from ls.utils import verify_link_exist

redirect_url = Blueprint("redirect", __name__)

shortener_domain = get_shortener_domain()


@redirect_url.route("/<path:path>", host=shortener_domain)
def make_redirect(path: str) -> Response | tuple[str, int]:
    """

    :param path: The fetched path
    :return: The redirection
    """
    if verify_link_exist(path):
        db = get_db()
        query = db.execute("SELECT real_url from link WHERE url=?", (path,))
        return redirect(query.fetchall()[0][0])

    return render_template("404.html.j2"), 404


@redirect_url.route("/", host=shortener_domain)
def root_redirect() -> Response:
    """:return: Redirect to defined url"""
    return redirect(get_root_redirect())
