# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Application settings parser.
"""

import configparser
import dataclasses

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
                adafruit_key = adafruit.get('key')
                adafruit_username = adafruit.get('username')
                send_location = adafruit.getboolean('sendlocation', True)
                self.adafruit = Adafruit(adafruit_key, adafruit_username, send_location)
                self.location = None
                if "location" in config:
                    location = config['location']
                    latitude = location.get('latitude')
                    longitude = location.get('longitude')
                    if latitude is not None and longitude is not None:
                        self.location = Location(latitude, longitude)
                if self.location is None:
                    positionstack = config['positionstack']
                    token = positionstack.get('token')
                    query = positionstack.get('query')
                    region = positionstack.get('region')
                    country = positionstack.get('country')
                    self.positionstack = Positionstack(token, query, region, country)
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
    def geocoding_token(self):
        """
        Get the Positionstack.com token
        """
        return self.positionstack.token

    @property
    def query(self):
        """
        Get the Positionstack.com query
        """
        return self.positionstack.query

    @property
    def region(self):
        """
        Get the Positionstack region
        """
        return self.positionstack.region

    @property
    def country(self):
        """
        Get the Positionstack.com country
        """
        return self.positionstack.country

    @property
    def adafruit_key(self):
        """
        Get the Adafruit.IO API key
        """
        return self.adafruit.key

    @property
    def adafruit_username(self):
        """
        Get the Adafruit.IO API username
        """
        return self.adafruit.username

    @property
    def send_location(self):
        """
        Get the locationdata flag
        """
        return self.adafruit.send_location

    @property
    def latitude(self):
        """
        Get the latitude
        """
        return self.location.latitude

    @property
    def longitude(self):
        """
        Get the longitude
        """
        return self.location.longitude

    def has_location(self):
        """
        Determine whether location data is present
        """
        return self.location is not None
