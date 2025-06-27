#! /bin/sh

if [ -z "$MQTT_HOST" ]; then
    >&2 echo "MQTT_HOST environment variable is not set"
    exit 1
fi

export APP=`pwd`

$(dirname $0)/update-assets.sh

/usr/bin/env python3 << EOF
import os
import asyncio

from hass_victron_mqtt_discovery import HassVictronMqttDiscovery

async def main():
    hass_discovery = HassVictronMqttDiscovery(
        mqtt_host = os.environ['MQTT_HOST'],
        mqtt_port = int(os.environ.get('MQTT_PORT', 1883)),
        mqtt_username = os.environ.get('MQTT_USERNAME', None),
        mqtt_password = os.environ.get('MQTT_PASSWORD', None),
        mqtt_prefix = os.environ.get('MQTT_PREFIX', ''),
        hass_status_topic = os.environ.get('HASS_STATUS_TOPIC', 'homeassistant/status'),
        registers_path = './assets/modbus-registers.xlsx',
        sensor_documentation_path = './assets/sensor-documentation.html',
    )

    await hass_discovery.start()

asyncio.run(main())
EOF
