# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Temperature Monitor
"""

import signal
import sys
import time
from typing import NoReturn

import board
import adafruit_bmp3xx

from eprint import eprint
from settings import Settings
from positionstack import Positionstack
from opentopodata import OpenTopoData
from aio_logger import AIOLogger

class TemperatureMonitor:
    """
    Temperature Monitor
    """
    _FEED_GROUP = "outdoor"
    _TEMPERATURE_FEED = "temperature"
    _PRECISION = 1

    def __init__(self) -> None:
        self.settings = Settings('config.ini')
        self.settings.dump()
        if self.settings.send_location:
            if self.settings.has_location():
                latitude = self.settings.latitude
                longitude = self.settings.longitude
            else:
                ps = Positionstack(self.settings.geocoding_token)
                latitude, longitude, _label = ps.forward_geocode(
                    self.settings.query,
                    self.settings.region,
                    self.settings.country
                )
            otd = OpenTopoData()
            elevation = otd.get_elevation(latitude, longitude)
            self.aio_logger = AIOLogger(
                self.settings.adafruit_username,
                self.settings.adafruit_key,
                group_name=self._FEED_GROUP
            )
            self.aio_logger.set_metadata(latitude, longitude, elevation)
        self.aio_logger.get_feed(self._TEMPERATURE_FEED)
        i2c = board.I2C()
        self.sensor = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    def log_temperature(self) -> None:
        """
        Log the current temperature.
        """
        temperature = round(self.sensor.temperature, self._PRECISION)
        self.aio_logger.log(self._TEMPERATURE_FEED, temperature)
        eprint("Temperature recorded:", temperature)

def main() -> NoReturn:
    """
    Entry point function when run from command line.
    """
    def signal_handler(*args):
        """
        Handle various signals
        """
        signum = args[0]
        eprint(f'Handling signal {signum} ({signal.Signals(signum).name}).')
        if signum in (signal.SIGINT, signal.SIGTERM):
            sys.exit(0)
        else:
            eprint("Unknown signal received.")

    monitor = TemperatureMonitor()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    while True:
        monitor.log_temperature()
        time.sleep(60)

if __name__ == '__main__':
    main()
