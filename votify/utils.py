from __future__ import annotations

import requests


def check_response(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.HTTPError:
        _raise_response_exception(response)


def _raise_response_exception(response: requests.Response):
    raise Exception(
        f"Request failed with status code {response.status_code}: {response.text}"
    )
