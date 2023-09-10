"""Launch & init flask app."""

import contextlib
from pathlib import Path

from flask import Flask
from flask_login import LoginManager

from .admin.user import User
from .config import get_config_dict
from .db import get_db


def create_app() -> Flask:
    """
    See https://flask-login.readthedocs.io/en/latest/#installation
    :return: Flask.
    """
    app = Flask(__name__)
    app.run(host="::", port=5000, debug=True)
    config_dict = get_config_dict()
    app.config.update(
        {
            "DATABASE": config_dict["database"],
            "SECRET_KEY": config_dict["secret_key"],
            "DEBUG": config_dict["debug"],
            "ADMIN_DOMAIN": config_dict["admin_domain"],
            "SHORTENER_DOMAIN": config_dict["shortener_domain"],
        }
    )

    from . import db

    db.init_app(app)
    with contextlib.suppress(OSError):
        Path.mkdir(app.instance_path, parents=True)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: int) -> User:
        project_db = get_db()
        curs = project_db.cursor()
        curs.execute("SELECT * from user where id = (?)", [user_id])
        lu = curs.fetchone()
        if lu is None:
            return None
        return User(int(lu[0]), lu[1], lu[2])

    from ls.admin.admin import admin as admin_blueprint
    from ls.admin.auth import auth as auth_blueprint

    from .redirect import redirect_url as redirect_blueprint

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(auth_blueprint, cli_group=None)
    app.register_blueprint(redirect_blueprint)

    return app
