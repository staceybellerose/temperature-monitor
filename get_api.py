# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper for GET API calls.
"""

import json
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
from typing import Any
from collections.abc import Callable

from eprint import eprint

class GetApi:
    """
    Wrapper for GET API calls.
    """

    def build_url(self, base: str, endpoint: str, params: dict) -> str:
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
        HTTPError: when the server can't fulfill the request.
        URLError: when the server can't be reached.
        """
        try:
            with urllib.request.urlopen(url) as response:
                value = response.read()
                json_data = json.loads(value.decode("utf-8"))
                return json_parser(json_data)
        except HTTPError as e:
            eprint("The server couldn't fulfill the request.")
            eprint("Error code:", e.code)
            raise e
        except URLError as e:
            eprint("We failed to reach a server.")
            eprint("Reason:", e.reason)
            raise e
