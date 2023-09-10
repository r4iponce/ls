"""User management class."""
# ruff: noqa: ANN101, ANN001, D102, ANN201, D103
from flask_login import UserMixin

from ls.db import get_db


class User(UserMixin):
    """Class with user data."""

    def __init__(self, user_id, name, password) -> None:
        self.user_id = user_id
        self.name = name
        self.password = password
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.user_id

    def get_name(self):
        return self.name


def load_user(user_id: int) -> User:
    db = get_db()
    curs = db.cursor()
    curs.execute("SELECT * from user where id = (?)", [user_id])
    lu = curs.fetchone()
    if lu is None:
        return None
    return User(int(lu[0]), lu[1], lu[2])
