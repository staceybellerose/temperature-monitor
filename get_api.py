# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper for GET API calls.
"""

import urllib.parse
from typing import Any, Dict
from collections.abc import Callable

from urllib3.util import Retry
import requests
from requests.adapters import HTTPAdapter

from eprint import eprint

class GetApi:
    """
    Wrapper for GET API calls.
    """
    def __init__(self, proxies=None) -> None:
        """
        Initialize the API.

        Parameters
        ----------
        proxies: a dict of proxies to be used by the requests library.
        """
        self.session = requests.Session()
        self.session.proxies = proxies
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        self.session.mount('http://', HTTPAdapter(max_retries=retry_strategy))

    def build_url(self, base: str, endpoint: str, params: Dict) -> str:
        """
        Get the appropriately formatted url for the endpoint.

        Parameters
        ----------
        base: The API base URL.
        endpoint: The API endpoint.
        params: A dictionary containing the query parameters.

        Returns
        -------
        A string containing the full GET url to call for the endpoint.
        """
        sep = "/" if base[-1:] != "/" and endpoint[:1] != "/" else ""
        return base + sep + endpoint + "?" + urllib.parse.urlencode(params)

    def call_get_api(self, url: str, json_parser: Callable[[Any], Any]):
        """
        Call the GET API and return a result.

        Parameters
        ----------
        url: The GET API to call.
        json_parser: A function which parses the json response and returns the desired data.

        Returns
        -------
        The result of the parse_json() method applied to the json returned
        from the API call.

        Raises
        ------
        ConnectionError: when the server can't be reached.
        RequestException: when the server can't fulfill the request.
        ValueError: when the server doesn't return parsable JSON data.
        """
        try:
            response = self.session.get(url)
            json_data = response.json()
            return json_parser(json_data)
        except ValueError as e:
            eprint("Unable to parse JSON response.")
            raise e
        except requests.ConnectionError as e:
            eprint("We failed to reach a server.")
            raise e
        except requests.RequestException as e:
            eprint("The server couldn't fulfill the request.")
            raise e
