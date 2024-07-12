"""Sqlite3 database management, use get_db() for connection."""

import sqlite3

import werkzeug
from flask import Flask, current_app, g
from flask.app import T_teardown

from ls.db.user import User


def get_db() -> sqlite3.Connection:
    """
    Connection to sqlite3 database
    :return: sqlite3.Connection object https://docs.python.org/3/library/sqlite3.html#connection-objects.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e: T_teardown | None = None) -> None:  # noqa: ARG001
    """
    Close database (https://flask.palletsprojects.com/en/1.1.x/tutorial/database/#id1)
    :param e: Error object
    :return: None.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> None:
    """
    Initialise database with schema.sql, wipe all before
    :return: None.
    """
    db = get_db()

    with current_app.open_resource("../sql/schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def init_app(app: Flask) -> None:
    """
    https://flask.palletsprojects.com/en/1.1.x/tutorial/database/#register-with-the-application
    :param app: a Flask object
    :return: None.
    """
    app.teardown_appcontext(close_db)


def list_users() -> list[User]:
    """Get all users."""
    db = get_db()
    curs = db.cursor()
    curs.execute("SELECT * from user")
    query_result = curs.fetchall()

    return [User(int(i[0]), i[1], i[2]) for i in query_result]


def get_user(user_id: int) -> User | None:
    """
    Get a user
    :param user_id: ID of user to fetch.
    :return: A user.
    """
    db = get_db()
    curs = db.cursor()
    curs.execute("SELECT * from user where id = (?)", [user_id])
    lu = curs.fetchone()
    if lu is None:
        return None
    return User(int(lu[0]), lu[1], lu[2])


def create_user(user: str, password: str) -> None:
    """
    Create a user.
    :param user: username
    :param password: password of user
    :return: None.
    """
    hashed_password = werkzeug.security.generate_password_hash(
        password, method="scrypt:65536:8:2"
    )
    db = get_db()
    db.execute(
        "INSERT INTO user(name, password) VALUES (?, ?)",
        (user.lower(), hashed_password),
    )
    db.commit()


def delete_user(user: str) -> None:
    """
    Delete a user
    :param user: username
    :return: None.
    """
    db = get_db()
    db.execute(
        "DELETE FROM user WHERE name=?",
        (user.lower(),),
    )
    db.commit()


def verify_link_exist(url: str) -> bool:
    """
    Verify if an url already exist in database.
    :param url: redirect source url
    :return: Bool, true if existed, else false.
    """
    db = get_db()
    query = db.execute("SELECT EXISTS(SELECT * FROM link  WHERE url=?)", (url,))
    result = query.fetchall()
    return result[0][0] == 1


def get_link(url: str) -> str:
    """
    Get a link from database
    :param url: redirect source url.
    """
    db = get_db()
    query = db.execute("SELECT real_url from link WHERE url=?", (url,))
    return query.fetchall()[0][0]
