# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Application settings parser.
"""

import configparser

from eprint import eprint

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
                positionstack = config['positionstack']
                self._geocoding_token = positionstack.get('token')
                self._query = positionstack.get('query')
                self._country = positionstack.get('country')

                adafruit = config['adafruit']
                self._adafruit_key = adafruit.get('key')
                self._adafruit_username = adafruit.get('username')
            except configparser.Error as exc:
                raise RuntimeError(
                    "ERR: Invalid settings file. Please use config.ini.sample to create a\nproperly formatted file."
                ) from exc
        if len(self._geocoding_token) == 0:
            raise RuntimeError(
                "ERR: You need to set your PositionStack token first. If you\ndon't already have one, you can register for a free account at\nhttps://positionstack.com/signup/free"
            )
        if len(self._adafruit_key) == 0 or len(self._adafruit_username) == 0:
            raise RuntimeError(
                "ERR: You need to set your Adafruit IO key and username first.\nIf you don't already have one, you can register for a free account at\nhttps://io.adafruit.com/"
            )

    def dump(self):
        """
        Dump the parsed settings file to stderr for debugging.
        """
        eprint("Parsed settings file")
        eprint("Location to look up:", self._query, self._country)

    @property
    def geocoding_token(self):
        """
        Get the PositionStack.com token
        """
        return self._geocoding_token

    @property
    def query(self):
        """
        Get the PositionStack.com query
        """
        return self._query

    @property
    def country(self):
        """
        Get the PositionStack.com country
        """
        return self._country

    @property
    def adafruit_key(self):
        """
        Get the Adafruit.IO API key
        """
        return self._adafruit_key

    @property
    def adafruit_username(self):
        """
        Get the Adafruit.IO API username
        """
        return self._adafruit_username
