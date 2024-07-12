"""User management cli."""

import click
from flask import Blueprint

from ls import User
from ls.admin.auth import verify_user_exist
from ls.config.config import get_minimum_password_length
from ls.db.db import create_user, delete_user, list_users

user_cli = Blueprint("user-cli", __name__)


@user_cli.cli.command("list")
def list_users_command() -> None:
    """List all users."""
    users: list[User] = list_users()
    first: bool = True
    msg = ""
    for user in users:
        if first:
            msg += f"{user.name}"
            first = False
        else:
            msg += f"\n{user.name}"

    click.echo(msg)


@user_cli.cli.command("create", help="Create a new user")
@click.argument("user")
@click.option("--password", "-p", prompt=True, help="Password for the user")
def create_user_command(user: str, password: str) -> None:
    """
    Cli command for create a user
    :param user: username of the new user
    :param password: password of the new user
    :return: None.
    """
    if verify_user_exist(user):
        click.echo("User already exists")
        return

    if len(password) <= get_minimum_password_length() or len(password) > 1024:
        click.echo("Password must be between 1 and 1024 characters")
        return

    create_user(user, password)
    click.echo(f"User {user} created")


@user_cli.cli.command("delete", help="Delete a user")
@click.argument("user")
@click.option("--force", "-f", default=False, is_flag=True,
              help="Remove confirmation")
def delete_user_command(user: str, force: bool) -> None:  # noqa: FBT001
    """
    Cli command for delete user
    :param user: username of user to delete
    :param force: remove confirmation
    :return: None.
    """
    if verify_user_exist(user):
        if force:
            delete_user(user)
            return
        if input(f"You really want to delete {user} ? (yes or no) : ") == "yes":
            delete_user(user)
    else:
        click.echo("User not exist, nothing to do")
