# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Application settings parser.
"""

import configparser
import dataclasses
from typing import Optional

from eprint import eprint

@dataclasses.dataclass
class Location:
    """
    Location data
    """
    latitude: float
    longitude: float


@dataclasses.dataclass
class Adafruit:
    """
    Metadata for Adafruit.IO account
    """
    key: str
    username: str
    send_location: bool


@dataclasses.dataclass
class Positionstack:
    """
    Metadata for Positionstack account
    """
    token: str
    query: str
    region: str
    country: str


class Settings:
    """
    A class to read a settings/ini file and parse the required values.
    """
    def __init__(self, inifilepath: str):
        """
        Parameters
        ----------
        inifilepath: A string containing a path to the settings file.
        """
        config = configparser.ConfigParser()
        with open(inifilepath, encoding="utf-8") as file:
            config.read_file(file)
            try:
                adafruit = config['adafruit']
                self.adafruit = Adafruit(
                    adafruit.get('key'),
                    adafruit.get('username'),
                    adafruit.getboolean('sendlocation', True)
                )
                self.location: Optional[Location] = None
                if "location" in config:
                    location = config['location']
                    latitude = location.getfloat('latitude', fallback=None)
                    longitude = location.getfloat('longitude', fallback=None)
                    if latitude is not None and longitude is not None:
                        self.location = Location(latitude, longitude)
                if self.location is None:
                    positionstack = config['positionstack']
                    self.positionstack = Positionstack(
                        positionstack.get('token'),
                        positionstack.get('query'),
                        positionstack.get('region'),
                        positionstack.get('country')
                        )
            except configparser.Error as exc:
                raise RuntimeError(
                    "ERR: Invalid settings file. Please use config.ini.sample to create a\nproperly formatted file."
                ) from exc
        if (
            self.adafruit.send_location
            and self.location is None
            and len(self.positionstack.token) == 0
        ):
            raise RuntimeError(
                "ERR: You need to set your PositionStack token first. If you\ndon't already have one, you can register for a free account at\nhttps://positionstack.com/signup/free"
            )
        if len(self.adafruit.key) == 0 or len(self.adafruit.username) == 0:
            raise RuntimeError(
                "ERR: You need to set your Adafruit IO key and username first.\nIf you don't already have one, you can register for a free account at\nhttps://io.adafruit.com/"
            )

    def dump(self):
        """
        Dump the parsed settings file to stderr for debugging.
        """
        eprint("Parsed settings file")
        if self.location is not None:
            eprint("Location to use:", self.location.latitude, self.location.longitude)
        else:
            eprint(
                "Location to look up:",
                self.positionstack.query,
                self.positionstack.region,
                self.positionstack.country
            )

    @property
    def geocoding_token(self) -> str:
        """
        Get the Positionstack.com token
        """
        return self.positionstack.token

    @property
    def query(self) -> str:
        """
        Get the Positionstack.com query
        """
        return self.positionstack.query

    @property
    def region(self) -> str:
        """
        Get the Positionstack region
        """
        return self.positionstack.region

    @property
    def country(self) -> str:
        """
        Get the Positionstack.com country
        """
        return self.positionstack.country

    @property
    def adafruit_key(self) -> str:
        """
        Get the Adafruit.IO API key
        """
        return self.adafruit.key

    @property
    def adafruit_username(self) -> str:
        """
        Get the Adafruit.IO API username
        """
        return self.adafruit.username

    @property
    def send_location(self) -> bool:
        """
        Get the locationdata flag
        """
        return self.adafruit.send_location

    @property
    def latitude(self) -> float:
        """
        Get the latitude
        """
        if self.location is not None:
            return self.location.latitude
        return float('nan')

    @property
    def longitude(self) -> float:
        """
        Get the longitude
        """
        if self.location is not None:
            return self.location.longitude
        return float('nan')

    def has_location(self) -> bool:
        """
        Determine whether location data is present
        """
        return self.location is not None
