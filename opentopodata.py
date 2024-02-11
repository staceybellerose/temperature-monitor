# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper for OpenTopoData.org API.
"""

from get_api import GetApi
from eprint import eprint

class OpenTopoData(GetApi):
    """
    OpenTopoData Wrapper.
    """

    _BASE_URL = "https://api.opentopodata.org/v1"
    _DATASETS = [
        "nzdem8m", # New Zealand
        "ned10m", # USA
        "eudem25m", # Europe
        "mapzen" # Global
    ]
    _ENDPOINT = ",".join(_DATASETS)

    def _parse_json(self, json_data):
        """
        Parse the OpenTopoData elevation API endpoint JSON data and
        return the elevation.

        Parameters
        ----------
        json_data: The JSON data received from the API endpoint.

        Returns
        -------
        The elevation returned from the API endpoint, as a float.
        """
        data = json_data["results"][0]
        elevation = data["elevation"]
        eprint("Elevation lookup successful:", elevation)
        return elevation

    def get_elevation(self, latitude: float, longitude: float) -> float:
        """
        Call the elevation API endpoint from opentopodata.org and
        return the elevation of the location.

        Parameters
        ----------
        latitude: The latitude of the location.
        longitude: The longitude of the location.

        Raises
        ------
        HTTPError: when the server can't fulfill the request.
        URLError: when the server can't be reached.
        """
        params = {"locations": f"{latitude},{longitude}"}
        url = self.build_url(self._BASE_URL, self._ENDPOINT, params)
        return self.call_get_api(url, self._parse_json)
