from flask import Blueprint, redirect
from .db import get_db

redirect_url = Blueprint("redirect", __name__)


@redirect_url.route("/", defaults={"path": ""}, host="localhost")
@redirect_url.route("/<path:path>", host="localhost")
def make_redirect(path):
    db = get_db()
    query = db.execute("SELECT real_url from link WHERE url=?", (path,))
    return redirect(query.fetchall()[0][0])
