# SPDX-FileCopyrightText: © 2022, 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Wrapper class for Adafruit.IO.
"""

from datetime import datetime, timezone
import dataclasses

from Adafruit_IO import Client, Group, Feed, AdafruitIOError

from eprint import eprint

@dataclasses.dataclass
class Metadata:
    """
    Metadata to record at Adafruit.IO along with data from feed.
    """
    lat: float
    lon: float
    ele: float


class AIOLogger:
    """
    Adafruit.IO API Client wrapper.
    """
    def __init__(self, aio_user: str, aio_key: str, group_name: str = "Default"):
        """
        Parameters
        ----------
        aio_user: Username for Adafruit.IO.
        aio_key: Authentication Key for Adafruit.IO.
        group_name: Name of group to use at Adafruit.IO.
        """
        self.aio = Client(aio_user, aio_key)
        self.group = self.get_feed_group(group_name)
        self.feeds = self.aio.feeds()
        self.metadata: Metadata = None

    def set_metadata(self, latitude=None, longitude=None, elevation=None):
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

    def log(self, feed_name, datapoint):
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
        except AdafruitIOError:
            eprint(f"WARN: Unable to transmit data ({datapoint}) to feed {feed_key} - skipped.")
