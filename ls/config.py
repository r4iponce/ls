"""
Import config item from a yaml
"""
from os import getenv

import yaml


def get_config_file() -> str:
    """
    Fetch config file path from variable, use config.yml per default
    :return: config file path
    """
    if getenv("LS_CONFIG_PATH") is not None:
        return getenv("LS_CONFIG_PATH")
    else:
        return "config.yml"


def get_config_dict() -> dict:
    """
    :return: A dict with each item in yaml
    """
    with open(get_config_file(), "r") as config:
        config = yaml.safe_load(config)
    return config
