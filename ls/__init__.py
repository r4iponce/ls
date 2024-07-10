"""Launch & init flask app."""

import contextlib
from pathlib import Path

from flask import Flask
from flask_login import LoginManager

from ls.admin.user import User
from ls.config import get_config
from ls.db import get_db


def create_app() -> Flask:
    """
    See https://flask-login.readthedocs.io/en/latest/#installation
    :return: Flask.
    """
    app = Flask(__name__)
    config = get_config()

    app.run(host="::", port=config.listen_port, debug=config.debug)
    app.config.update(
        {
            "DATABASE": config.database,
            "SECRET_KEY": config.secret_key,
            "ADMIN_DOMAIN": config.admin_domain,
            "SHORTENER_DOMAIN": config.shortener_domain,
        }
    )

    from . import db

    db.init_app(app)
    with contextlib.suppress(OSError):
        path = Path(app.instance_path)
        Path.mkdir(path, parents=True)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: int) -> User | None:
        project_db = get_db()
        curs = project_db.cursor()
        curs.execute("SELECT * from user where id = (?)", [user_id])
        lu = curs.fetchone()
        if lu is None:
            return None
        return User(int(lu[0]), lu[1], lu[2])

    from ls.admin.admin import admin as admin_blueprint
    from ls.admin.auth import auth as auth_blueprint
    from ls.redirect import redirect_url as redirect_blueprint

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(auth_blueprint, cli_group=None)
    app.register_blueprint(redirect_blueprint)

    return app
