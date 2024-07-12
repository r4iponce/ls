"""Import config item from a toml."""

import tomllib
from dataclasses import dataclass
from os import getenv
from pathlib import Path


@dataclass
class Config:
    """Configuration object for ls."""

    database: str
    secret_key: str
    debug: bool
    admin_domain: str
    shortener_domain: str
    listen_port: int
    minimum_password_length: int
    root_redirect: str


def get_config_file() -> str:
    """
    Fetch config file path from variable, use config.toml per default
    :return: config file path.
    """
    if getenv("LS_CONFIG_PATH") is not None:
        return getenv("LS_CONFIG_PATH")
    return "config.toml"


def get_config() -> Config:
    """:return: A dict with each item in toml"""
    with Path(get_config_file()).open("rb") as f:
        loaded_dict: dict = tomllib.load(f)

    config = Config(**loaded_dict)

    if "minimum_password_length" not in loaded_dict:
        config.minimum_password_length = 12
    return config


def get_shortener_domain() -> str:
    """:return: shortener_domain from config"""
    return get_config().shortener_domain


def get_admin_domain() -> str:
    """:return: admin_domain from config"""
    return get_config().admin_domain


def get_root_redirect() -> str:
    """:return: root_redirect from config"""
    return get_config().root_redirect


def get_minimum_password_length() -> int:
    """:return: Configured minimum password length, default is 12"""
    return get_config().minimum_password_length
