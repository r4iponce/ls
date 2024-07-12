"""DB management cli."""

import click
from flask import Blueprint

from ls.db.db import init_db

db_cli = Blueprint("db-cli", __name__)


@db_cli.cli.command("init", help="Initialise database")
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
