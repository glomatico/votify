from __future__ import annotations

from pathlib import Path

import click
import colorama
import requests

from .constants import X_NOT_FOUND_STRING


def check_response(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.HTTPError:
        _raise_response_exception(response)


def _raise_response_exception(response: requests.Response):
    raise Exception(
        f"Request failed with status code {response.status_code}: {response.text}"
    )


def prompt_path(path_description: str, path_obj: Path) -> Path:
    while not path_obj.exists():
        path_obj_str = click.prompt(
            X_NOT_FOUND_STRING.format(path_description, path_obj.absolute())
            + ". Move it to that location or drag and drop it here. Then, press enter to continue",
            default=str(path_obj),
            show_default=False,
        )
        path_obj = Path(path_obj_str.strip('"'))
    return path_obj


def color_text(text: str, color) -> str:
    return color + text + colorama.Style.RESET_ALL
