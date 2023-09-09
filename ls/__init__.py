from flask import Flask, Config
from .config import get_config_dict
import os


def create_app() -> None:
    """
    See https://flask-login.readthedocs.io/en/latest/#installation
    :return: None
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
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .admin import admin as admin_blueprint
    from .redirect import redirect_url as redirect_blueprint

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(redirect_blueprint)

    return app
