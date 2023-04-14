"""Read a text file (for example, the body of an email) and add the first URL found to Pocket."""

from __future__ import annotations

import datetime
import os
import pathlib
import re
from typing import Any

import click
import requests
import toml
from rich import print
from xdg import xdg_config_home, xdg_data_home

__version__ = "0.1.0"

# constants
APP_NAME = "put_in_pocket"
POCKET_CONSUMER_KEY = "POCKET_CONSUMER_KEY"  # environment variable
POCKET_ACCESS_TOKEN = "POCKET_ACCESS_TOKEN"  # environment variable

# global variables
_global_log = True
_global_verbose = False


def log(msg: str) -> None:
    """Log a message to the app log if _global_log = True."""
    global _global_log
    if not _global_log:
        return
    log_file = get_log_file()
    with log_file.open("a") as f:
        timestamp = datetime.datetime.now().isoformat()
        f.write(f"{timestamp} - {msg}\n")


def verbose(msg: str) -> None:
    """Print a message to stdout if _global_verbose = True and logs it to the app log if _global_log = True"""
    global _global_verbose
    global _global_log
    if _global_log:
        log(msg)
    if _global_verbose:
        print(msg)


def get_data_dir() -> pathlib.Path:
    """Get the directory where data files are stored; create it if necessary."""
    data_dir = xdg_data_home() / APP_NAME
    if not data_dir.is_dir():
        data_dir.mkdir(parents=True)
    return data_dir


def get_log_file() -> pathlib.Path:
    """Get the path to the log file; create it if necessary."""
    log_file = get_data_dir() / f"{APP_NAME}.log"
    if not log_file.is_file():
        log_file.touch()
    return log_file


def get_config_dir() -> pathlib.Path:
    """Get the directory where config files are stored; create it if necessary."""
    config_dir = xdg_config_home() / APP_NAME
    if not config_dir.is_dir():
        config_dir.mkdir(parents=True)
    return config_dir


def get_config_file() -> pathlib.Path:
    """Get the path to the config file; create it if necessary."""
    config_file = get_config_dir() / "config.toml"
    if not config_file.is_file():
        config_file.touch()
    return config_file


def load_config() -> dict[str, Any]:
    """Load the configuration file."""
    config_file = get_config_file()
    with open(config_file) as f:
        config = toml.load(f)

    if os.environ.get("POCKET_CONSUMER_KEY"):
        config["consumer_key"] = os.environ.get("POCKET_CONSUMER_KEY")
    if os.environ.get("POCKET_ACCESS_TOKEN"):
        config["access_token"] = os.environ.get("POCKET_ACCESS_TOKEN")

    return config


def save_config(config: dict[str, Any]):
    """Save the configuration file."""
    config_file = get_config_file()
    with open(config_file, "w") as f:
        toml.dump(config, f)


def get_url_from_text(text: str) -> str | None:
    """
    Extracts the first URL found in the text.

    Args:
        text (str): The text to search for URLs.

    Returns:
        str: The first URL found in the text, or None if no URL is found.
    """

    # I was surprised at how difficult it was to find a regex that would match URLs
    # and that there was apparently no canonical solution. I found this one at
    # https://github.com/MJNinja/detect-url-inside-string/blob/master/url_detect.php
    # and it appears to work well enough in all my tests
    # pull-requests happily accepted for a better solution
    url_pattern = re.compile(
        r"(?i)\b((?:https?:\/\/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    )
    return match[0] if (match := url_pattern.search(text)) else None


def add_url_to_pocket(url: str, consumer_key: str, access_token: str) -> dict[str, Any]:
    """
    Adds a URL to a user's Pocket account using the Pocket API.

    Args:
        url (str): The URL to add to Pocket.
        consumer_key (str): The Pocket API consumer key.

    Returns:
        dict: The response from the Pocket API.
    """
    endpoint = "https://getpocket.com/v3/add"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Accept": "application/json",
    }
    data = {"url": url, "consumer_key": consumer_key, "access_token": access_token}
    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()


def get_request_token(consumer_key: str, redirect_uri: str) -> str:
    """Get Pocket API request token from user."""
    endpoint = "https://getpocket.com/v3/oauth/request"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Accept": "application/json",
    }
    data = {"consumer_key": consumer_key, "redirect_uri": redirect_uri}
    response = requests.post(endpoint, headers=headers, json=data)
    try:
        return response.json()["code"]
    except Exception as e:
        raise ValueError(f"Error getting request token from Pocket API: {e}") from e


def authenticate_with_pocket(consumer_key: str, redirect_uri: str) -> str:
    """
    Authenticates a command line Python app with Pocket using the Pocket API to get a request token.

    Args:
        consumer_key (str): The Pocket API consumer key.
        redirect_uri (str): The redirect URI to use for authentication.

    Returns:
        str: The request token.
    """
    request_token = get_request_token(consumer_key, redirect_uri)
    authentication_url = f"https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={redirect_uri}"
    input(f"Open this URL in your browser to authenticate:\n{authentication_url}\n")
    input("Press Enter to continue once you've authenticated.")
    return request_token


def get_access_token(consumer_key, request_token):
    """Get user's Pocket API access token."""
    access_token_url = "https://getpocket.com/v3/oauth/authorize"
    payload = {"consumer_key": consumer_key, "code": request_token}
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Accept": "application/json",
    }
    response = requests.post(access_token_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    raise ValueError(f"Error getting access token: {response.content}")


def get_consumer_key() -> str:
    """Get Pocket API consumer key from user."""
    print("You need to get a Pocket API consumer key.")
    print(
        "Go to https://getpocket.com/developer/apps/new and register a new app to get a consumer key."
    )
    if consumer_key := input("Enter the consumer key created in the step above: "):
        return consumer_key
    else:
        raise ValueError("No consumer key entered.")


def get_tokens_from_config(config: dict[str, Any]) -> tuple[str, str]:
    """Get consumer key and access token from config file."""
    if not config.get("pocket"):
        consumer_key = None
        access_token = None
    else:
        consumer_key = config["pocket"].get("consumer_key")
        access_token = config["pocket"].get("access_token")
    return consumer_key, access_token


def get_api_tokens() -> tuple[str, str, str]:
    """Get consumer key, access token, request token from config or from user"""
    config = load_config()
    consumer_key, access_token = get_tokens_from_config(config)

    redirect_uri = "https://www.google.com"
    if not consumer_key:
        print(
            f"consumer_key or access_token not found in config file at {get_config_file()} or in {POCKET_CONSUMER_KEY} environment variable."
        )
        get_consumer_key = get_consumer_key()

    if not access_token:
        print(
            f"consumer_key or access_token not found in config file at {get_config_file()} or in {POCKET_ACCESS_TOKEN} environment variable."
        )
        request_token = authenticate_with_pocket(consumer_key, redirect_uri)
        access_token = get_access_token(consumer_key, request_token)
    else:
        request_token = get_request_token(consumer_key, redirect_uri)

    config = {"pocket": {"consumer_key": consumer_key, "access_token": access_token}}
    save_config(config)

    return consumer_key, access_token, request_token


@click.command()
@click.version_option(version=__version__)
@click.option("--verbose", "verbose_", is_flag=True, default=False, help="Print verbose output.")
@click.option("--log/--no-log", "log_", is_flag=True, default=True, help=f"Log to file: {get_log_file()}.")
@click.option("--dry-run", is_flag=True, help="Dry run mode; don't add URL to Pocket.")
@click.argument("file_or_url")
@click.pass_context
def main(ctx: click.Context, dry_run: bool, verbose_: bool, log_: bool, file_or_url: str):
    """Add URL or the first URL found in a text FILE to Pocket."""

    if not file_or_url:
        click.echo(ctx.get_help())
        ctx.exit()

    global _global_log
    global _global_verbose
    _global_log = log_
    _global_verbose = verbose_

    consumer_key, access_token, _ = get_api_tokens()

    # Read the text file.
    if pathlib.Path(file_or_url).is_file():
        verbose(f"Reading text file: {file_or_url}")
        with open(file_or_url, "r") as f:
            text = f.read()
            url = get_url_from_text(text)
    else:
        # Assume the argument is a URL.
        url = get_url_from_text(file_or_url)

    if not url:
        verbose("No URL found in the text file.")
        ctx.exit(1)
    verbose(f"Found URL: '{url}'")

    # Add the URL to Pocket.
    if not dry_run:
        response = add_url_to_pocket(url, consumer_key, access_token)
        if response["status"] == 1:
            verbose(f"URL '{url}' added to Pocket: {response}")
        else:
            verbose(f"Error adding URL to Pocket: {response}")


if __name__ == "__main__":
    main()
