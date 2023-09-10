"""Import config item from a yaml."""
from os import getenv
from pathlib import Path

import yaml


def get_config_file() -> str:
    """
    Fetch config file path from variable, use config.yml per default
    :return: config file path.
    """
    if getenv("LS_CONFIG_PATH") is not None:
        return getenv("LS_CONFIG_PATH")
    return "config.yml"


def get_config_dict() -> dict:
    """:return: A dict with each item in yaml"""
    with Path.open(get_config_file()) as config:
        return yaml.safe_load(config)
