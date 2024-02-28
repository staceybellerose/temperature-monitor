# SPDX-FileCopyrightText: © 2022, 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper class for Adafruit.IO.
"""

from datetime import datetime, timezone
import dataclasses
import json
from typing import Any, Optional

from urllib3.util import Retry
from requests import RequestException, Session
from requests.adapters import HTTPAdapter
from Adafruit_IO import Client, Group, Feed, AdafruitIOError

from eprint import eprint

@dataclasses.dataclass
class Metadata:
    """
    Metadata to record at Adafruit.IO along with data from feed.
    """
    lat: Optional[float]
    lon: Optional[float]
    ele: Optional[float]


class AIOClient(Client):
    """
    Adafruit.IO Client wrapper to better handle request retries.
    """
    def __init__(self, username, key, proxies=None, base_url='https://io.adafruit.com'):
        super().__init__(username, key, proxies, base_url)
        self.session = Session()
        self.session.proxies = proxies
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        self.session.mount('http://', HTTPAdapter(max_retries=retry_strategy))

    def _build_headers(self, content_type: Optional[str] = None):
        headers = {'X-AIO-Key': self.key}
        if content_type is not None:
            headers['Content-Type'] = content_type
        return headers

    def _get(self, path, params=None):
        response = self.session.get(
            self._compose_url(path),
            headers=self._build_headers(),
            params=params
        )
        self._last_response = response
        self._handle_error(response)
        return response.json()

    def _post(self, path, data):
        response = self.session.post(
            self._compose_url(path),
            headers=self._build_headers('application/json'),
            data=json.dumps(data)
        )
        self._last_response = response
        self._handle_error(response)
        return response.json()

    def _delete(self, path):
        response = self.session.delete(
            self._compose_url(path),
            headers=self._build_headers('application/json')
        )
        self._last_response = response
        self._handle_error(response)


class AIOLogger:
    """
    Adafruit.IO API Data Logger.
    """
    def __init__(self, aio_user: str, aio_key: str, group_name: str = "Default"):
        """
        Parameters
        ----------
        aio_user: Username for Adafruit.IO.
        aio_key: Authentication Key for Adafruit.IO.
        group_name: Name of group to use at Adafruit.IO.
        """
        self.aio = AIOClient(aio_user, aio_key)
        self.group = self.get_feed_group(group_name)
        self.feeds = self.aio.feeds()
        self.metadata: Optional[Metadata] = None

    def set_metadata(
            self,
            latitude: Optional[float] = None,
            longitude: Optional[float] = None,
            elevation: Optional[float] = None
        ):
        """
        Set the metadata to use when posting to Adafruit.IO.

        Parameters
        ----------
        latitude: Latitude of the sensor.
        longitude: Longitude of the sensor.
        elevation: Elevation of the sensor.
        """
        self.metadata = Metadata(latitude, longitude, elevation)

    def get_feed_group(self, group_name: str) -> Group:
        """
        Get a Feed Group based on the group_name parameter, creating one if needed.

        Parameters
        ----------
        group_name: The name of the group to retrieve/create.

        Returns
        -------
        A Feed Group object.
        """
        group_list: list[Group] = self.aio.groups()
        for group in group_list:
            if group.name == group_name:
                return group
        # didn't find the feed group, so create it
        group = Group(name=group_name)
        return self.aio.create_group(group)

    def get_feed(self, feed_name: str) -> Feed:
        """
        Get a Feed object based on the feed_name parameter, creating one if needed.

        The Feed will be associated with our feed group.

        Parameters
        ----------
        feed_name: The name of the feed to retrieve/create.

        Returns
        -------
        A Feed object.
        """
        feed_key = f"{self.group.key}.{feed_name}"
        feed_list: list[Feed] = self.aio.feeds()
        for feed in feed_list:
            if feed.key == feed_key:
                return feed
        # didn't find the feed, so create it
        feed = Feed(name=feed_name)
        return self.aio.create_feed(feed, group_key=self.group.key)

    def log(self, feed_name: str, datapoint: Any):
        """
        Log data to Adafruit.IO.

        Parameters
        ----------
        feed_name: The name of the feed to which the data belongs.
        datapoint: The data to add to the feed.
        """
        if self.metadata is not None:
            metadata = dataclasses.asdict(self.metadata)
            metadata['created_at'] = datetime.now(timezone.utc).isoformat()
        else:
            metadata = None
        feed_key = f"{self.group.key}.{feed_name}"
        try:
            self.aio.send(feed_key, datapoint, metadata)
        except (AdafruitIOError, RequestException):
            eprint(f"WARN: Unable to transmit data ({datapoint}) to feed {feed_key} - skipped.")
