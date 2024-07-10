"""Sqlite3 database management, use get_db() for connection."""

import sqlite3

import click
from flask import Flask, current_app, g


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


def close_db(e=None) -> None:  # noqa: ANN001, ARG001
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


@click.command("init-db")
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """
    https://flask.palletsprojects.com/en/1.1.x/tutorial/database/#register-with-the-application
    :param app: a Flask object
    :return: None.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
