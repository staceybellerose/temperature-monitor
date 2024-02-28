# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

"""
Temperature Monitor.
"""

import dataclasses
import signal
import sys
import time
from typing import NoReturn

import board
import adafruit_bmp3xx
import adafruit_am2320

from eprint import eprint
from settings import Settings
from positionstack import Positionstack
from opentopodata import OpenTopoData
from aio_logger import AIOLogger


@dataclasses.dataclass
class Sensors:
    """
    Collection of sensors used in this project.
    """
    bmp388: adafruit_bmp3xx.BMP3XX_I2C
    am2320: adafruit_am2320.AM2320


class TemperatureMonitor:
    """
    Temperature Monitor.
    """
    _FEED_GROUP = "outdoor"
    _TEMPERATURE_FEED = "temperature"
    _PRESSURE_FEED = "pressure"
    _HUMIDITY_FEED = "humidity"
    _PRECISION = 1

    def __init__(self) -> None:
        self.settings = Settings('config.ini')
        self.settings.dump()
        self.aio_logger = AIOLogger(
            self.settings.adafruit_username,
            self.settings.adafruit_key,
            group_name=self._FEED_GROUP
        )
        if self.settings.send_location:
            if self.settings.has_location():
                latitude = self.settings.latitude
                longitude = self.settings.longitude
            else:
                positionstack = Positionstack(self.settings.geocoding_token)
                latitude, longitude, _label = positionstack.forward_geocode(
                    self.settings.query,
                    self.settings.region,
                    self.settings.country
                )
            otd = OpenTopoData()
            elevation = otd.get_elevation(latitude, longitude)
            self.aio_logger.set_metadata(latitude, longitude, elevation)
        self.aio_logger.get_feed(self._TEMPERATURE_FEED)
        self.aio_logger.get_feed(self._PRESSURE_FEED)
        self.aio_logger.get_feed(self._HUMIDITY_FEED)
        i2c = board.I2C()
        self.sensors = Sensors(
            adafruit_bmp3xx.BMP3XX_I2C(i2c),
            adafruit_am2320.AM2320(i2c)
        )

    def log_single_datum(self, datum: float, feed: str) -> None:
        """
        Log a single sensor datum to an Adafruit.IO feed.
        """
        rounded = round(datum, self._PRECISION)
        self.aio_logger.log(feed, rounded)

    def log_data(self) -> None:
        """
        Log the current sensor data.
        """
        try:
            temp2 = self.sensors.am2320.temperature
            self.log_single_datum(temp2, self._TEMPERATURE_FEED)
            humidity = self.sensors.am2320.relative_humidity
            self.log_single_datum(humidity, self._HUMIDITY_FEED)
            pressure = self.sensors.bmp388.pressure
            self.log_single_datum(pressure, self._PRESSURE_FEED)
            eprint(
                f"Sensor data recorded: {temp2:.1f} °C, {humidity:.1f} %RH, {pressure:.1f} hPa"
            )
        except OSError as exc:
            eprint("Unable to read sensor.", exc.strerror, sep="\n")

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
        monitor.log_data()
        time.sleep(60)

if __name__ == '__main__':
    main()
