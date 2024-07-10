"""Import config item from a yaml."""

from os import getenv
from pathlib import Path

import yaml


def get_config_file() -> str:
    """
    Fetch config file path from variable, use config.yaml per default
    :return: config file path.
    """
    if getenv("LS_CONFIG_PATH") is not None:
        return getenv("LS_CONFIG_PATH")
    return "config.yaml"


def get_config_dict() -> dict:
    """:return: A dict with each item in yaml"""
    with Path.open(get_config_file()) as config:
        return yaml.safe_load(config)


def get_shortener_domain() -> str:
    """:return: shortener_domain from config"""
    return get_config_dict()["shortener_domain"]


def get_admin_domain() -> str:
    """:return: admin_domain from config"""
    return get_config_dict()["admin_domain"]


def get_root_redirect() -> str:
    """:return: root_redirect from config"""
    return get_config_dict()["root_redirect"]


def get_minimum_password_length() -> int:
    """:return: Configured minimum password length, default is 12"""
    if "minimum_password_length" in get_config_dict():
        return int(get_config_dict()["minimum_password_length"])
    return 12
