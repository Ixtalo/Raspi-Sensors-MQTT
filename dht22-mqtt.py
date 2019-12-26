#/usr/bin/env python3
"""

Raspi DHT22 MQTT

AST, 18.12.2018
Update: 26.12.2019

"""
import json
import sys
import paho.mqtt.client as mqtt
import Adafruit_DHT as dht


## load configuration from JSON file
config_filename = sys.argv[1]
with open(config_filename) as cfgf:
	config = json.load(cfgf)


## MQTT connection
client = mqtt.Client(client_id=config['mqtt_client_id'])
if config.get('mqtt_user') is not None:
	client.username_pw_set(username=config.get('mqtt_user'), password=config.get('mqtt_pass'))
client.connect(config.get('mqtt_host', 'localhost'), port=config.get('mqtt_port', 1883))
client.loop_start()


## DHT22 reading
humidity, temperature = dht.read_retry(dht.DHT22, config['dht_gpio'])
if humidity is not None:
	humidity = round(humidity, 1)
	client.publish(config['topics']['humidity'], humidity)
if temperature is not None:
	temperature = round(temperature, 1)
	client.publish(config['topics']['temperature'], temperature)


## MQTT sending message
client.loop_stop()
client.disconnect()
