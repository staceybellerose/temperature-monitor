# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper for PositionStack.com API.
"""

from get_api import GetApi
from eprint import eprint

class Positionstack(GetApi):
    """
    Wrapper for Positionstack.com API.
    """

    _BASE_URL = "http://api.positionstack.com/v1"
    _FORWARD = "forward"
    _REVERSE = "reverse"

    def __init__(self, token: str) -> None:
        """
        Initialize the API.

        Parameters
        ----------
        token: Your postitionstack API access key.
        """
        self.token = token

    def _get_url(self, endpoint: str, params: dict) -> str:
        """
        Get the appropriately formatted url for the endpoint.

        Parameters
        ----------
        endpoint: The API endpoint.
        params: A dictionary containing the query parameters.

        Returns
        -------
        A string containing the full GET url to call for the endpoint.
        """
        params["access_key"] = self.token
        return self.build_url(self._BASE_URL, endpoint, params)

    def _parse_forward_json(self, json_data) -> tuple[float, float, str]:
        """
        Parse the forward geocoding API endpoint JSON data.

        Parameters
        ----------
        json_data: The JSON data received from the API endpoint.

        Returns
        -------
        A tuple containing latitude, longitude, and label of location.
        """
        data = json_data["data"][0]
        latitude: float = data["latitude"]
        longitude: float = data["longitude"]
        label: str = data["label"]
        eprint("Geocoding lookup sucessful:", label)
        eprint("Latitude:", latitude, "Longitude:", longitude)
        return (latitude, longitude, label)

    def forward_geocode(
            self, query: str, region: str = None, country: str = None
        ) -> tuple[float, float, str]:
        """
        Call the forward geocoding API endpoint from postitionstack.com and
        return the location of the sent query.

        Parameters
        ----------
        query: Free-form location query (e.g. address, zip/postal code, city name, region name).
        region: Region name to filter results: district, city, state, administrative area, etc.
        country: Country code to filter results: either a 2- or 3-letter ISO-3166 Country Code.

        Returns
        -------
        A tuple containing latitude, longitude, and label of location.

        Raises
        ------
        HTTPError: when the server can't fulfill the request.
        URLError: when the server can't be reached.
        """
        params = {"query": query}
        if country is not None:
            params["country"] = country
        if region is not None:
            params["region"] = region
        url = self._get_url(self._FORWARD, params)
        return self.call_get_api(url, self._parse_forward_json)

    def _parse_reverse_json(self, json_data) -> dict:
        """
        Parse the forward geocoding API endpoint JSON data.

        Parameters
        ----------
        json_data: The JSON data received from the API endpoint.

        Returns
        -------
        A dict containing the location data.
        """
        data: dict = json_data["data"][0]
        label: str = data["label"]
        eprint("Reverse Geocoding lookup sucessful:", label)
        return data

    def reverse_geocode(self, latitude: float, longitude: float) -> dict:
        """
        Call the reverse geocoding API endpoint from postitionstack.com and
        return the location of the sent query.

        Parameters
        ----------
        latitude: The latitude for the query.
        longitude: The longitude for the query.

        Returns
        -------
        A dict containing the location data.

        Raises
        ------
        HTTPError: when the server can't fulfill the request.
        URLError: when the server can't be reached.
        """
        params = {"query": f"{latitude},{longitude}"}
        url = self._get_url(self._REVERSE, params)
        return self.call_get_api(url, self._parse_reverse_json)
