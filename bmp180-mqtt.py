#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bmp180-mqtt.py - Read BMP180 sensor data and publish values to MQTT.

Reads temperature and barometric pressure values from a BMP180 sensor
(attached to Rasperry Pi) and send the values to MQTT broker.

Usage:
  bmp180-mqtt.py <config.json>
  bmp180-mqtt.py -h | --help
  bmp180-mqtt.py --version

Arguments:
  config.json	  Configuration file in JSON format.

Options:
  -h --help       Show this screen.
  --version       Show version.
"""
##
## LICENSE:
##
## Copyright (C) 2019 Alexander Streicher
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
import os
import sys
from codecs import open
import json
import logging
import paho.mqtt.client as mqtt
from docopt import docopt
from paho.mqtt.client import MQTTMessageInfo

__version__ = "1.0"
__date__ = "2018-12-19"
__updated__ = "2019-12-29"
__author__ = "Ixtalo"
__license__ = "AGPL-3.0+"
__email__ = "ixtalo@gmail.com"
__status__ = "Production"

DEBUG = 0
TESTRUN = 0
PROFILE = 0
__script_dir = os.path.dirname(os.path.realpath(__file__))

### check for Python3
# if sys.version_info < (3, 0):
#    sys.stderr.write("Minimum required version is Python 3.x!\n")
#    sys.exit(1)


try:
    # noinspection PyUnresolvedReferences
    import Adafruit_BMP.BMP085 as BMP085
except ModuleNotFoundError:
    print("DHT library only works on a Raspi!")


def read_sensor():
    sensor = BMP085.BMP085()
    t = sensor.read_temperature()
    p = sensor.read_pressure()
    return t, p


def main():
    arguments = docopt(__doc__, version="raspi-bmp180-mqtt %s (%s)" % (__version__, __updated__))
    # print(arguments)

    ## setup logging
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.WARNING)

    ## determine config filename and path
    config_filename = arguments['<config.json>']
    if not os.path.isabs(config_filename):
        ## filename is not an absolute path, make it one based on this very script's directory
        config_filename = os.path.join(__script_dir, config_filename)

    ## load configuration from JSON file
    logging.info("Config file: %s", config_filename)
    with open(config_filename) as cfgf:
        config = json.load(cfgf)

    logging.debug("Configuration: %s", config)

    ## MQTT client
    client = mqtt.Client(client_id=config['mqtt_client_id'])
    if DEBUG:
        client.enable_logger(logging.getLogger("mqtt"))
    if config.get('mqtt_user') is not None:
        client.username_pw_set(username=config.get('mqtt_user'), password=config.get('mqtt_pass'))

    ## MQTT connection
    res_con = client.connect(config.get('mqtt_host', 'localhost'), port=config.get('mqtt_port', 1883))
    logging.debug("MQTT connect result: %d, %s", res_con, mqtt.error_string(res_con))

    if res_con != mqtt.MQTT_ERR_SUCCESS:
        logging.error("Could not connect to MQTT broker! (%d, %s)", res_con, mqtt.error_string(res_con))
    else:
        ## sensor reading
        temperature, pressure = read_sensor()

        ## MQTT sending message
        client.loop_start()
        client.publish(config['topics']['temperature'], temperature)
        client.publish(config['topics']['pressure'], pressure)
        client.loop_stop()

        ## MQTT disconnect
        res_discon = client.disconnect()
        logging.debug("MQTT disconnect: %d", res_discon)
        return res_discon

    return 0


if __name__ == "__main__":
    if DEBUG:
        # sys.argv.append("-v")
        # sys.argv.append("--debug")
        # sys.argv.append("-h")
        pass
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = __file__ + '.profile.bin'
        cProfile.run('main()', profile_filename)
        with open("%s.txt" % profile_filename, "wb") as statsfp:
            p = pstats.Stats(profile_filename, stream=statsfp)
            stats = p.strip_dirs().sort_stats('cumulative')
            stats.print_stats()
        sys.exit(0)
    sys.exit(main())
