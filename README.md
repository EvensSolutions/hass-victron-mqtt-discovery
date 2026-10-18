# Home Assistant MQTT discovery for Victron GX

[Victron GX MQTT](https://github.com/victronenergy/dbus-flashmq) integration that maps MQTT topics to [modbus registers](https://www.victronenergy.com/support-and-downloads/technical-information) and
uses this information to add [Home Assistant MQTT discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery).

The following functionality is implemented:

- Mapping MQTT topics to official modbus registers documentation.
- Expose MQTT topics as Home Assistant entities using MQTT discovery.
- Expose writable topics with correct Home Assistant entity type.
- Implement [Victron MQTT keep-alive](https://github.com/victronenergy/dbus-flashmq?tab=readme-ov-file#keep-alive) algorithm.

## Prerequisites

For this integration to work as expect you will need a few things:

- You to have the [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) installed and connect to your MQTT server / Victron GX Device.
- The MQTT feature is enabled in your Victron GX device. The setting is under `Settings > Services > MQTT Access`.
- This integration is packaged as a [Docker](https://docs.docker.com/engine/install/) container, you will need somewhere to run it.


## Usage

This project can be installed either as a Home Assistant Addon or as a Docker image.

### Home Assistant Addon

To install the addon you'll have to add this repository as a repository to your addons, and install the `Victron GX MQTT Discovery` integration.

- Open the [add-on store](https://my.home-assistant.io/redirect/supervisor_store/) on your instance.
- On the top right overflow menu, click on `Repositories`
- Add `https://github.com/EvensSolutions/hass-victron-mqtt-discovery` as a repository
- Click `Close`
- On the top right overflow menu, click on `Check for updates`
- Scroll to and click on `Victron GX MQTT Discovery`
- Click `Install`
- (optional) Configure your MQTT host in `Configuration`, if you use the MQTT add-on this will be auto-discovered.
- Click `Start`

### Docker

This project comes packaged as a docker container. Running this container will watch for GX devices publishing on the MQTT broker and automatically generate entities for the discovered GX entities.

Options can be provided as environment variables.

Only the `MQTT_HOST` environment variable is required, it should be set to the MQTT broker on which topics will be published.
If you do not run a separate MQTT broker `MQTT_HOST` should be set to the IP of your Victron GX.

```sh
docker run -ti \
    --restart=always \
    --name hass-victron-mqtt-discovery \
    -e MQTT_HOST=192.168.1.10 \
    ghcr.io/evenssolutions/hass-victron-mqtt-discovery:main
```

| Variable | Default | Description | Required |
| --- | --- | --- | --- |
| `MQTT_HOST` | | The address of the MQTT server to subscribe and publish to | Yes |
| `MQTT_PORT` | `1883` | The port on which the MQTT server runs | No |
| `MQTT_USERNAME` |  | The username used to authenticate to the MQTT server | No |
| `MQTT_PASSWORD` |  | The password used to authetnicate to the MQTT password | No |
| `MQTT_PREFIX` | `""` | The prefix to subscribe to. If you Victron data is published using a prefix, specify it here | No |
| `ASSET_MODBUS_REGISTERS_URL` | [link](https://www.victronenergy.com/upload/documents/CCGX-Modbus-TCP-register-list-3.50.xlsx) | The URL to the Victron provided list of modbus registers | No |
| `ASSET_SENSOR_DOCUMENTATION_URL` | [link](https://contributors.home-assistant.io/core/entities/sensor/) | The URL to the Home Assistant Sensor Entity documentation | No |

## Disclaimer

This project enables interaction with your Victron GX device using MQTT, based on official Victron documentation. It does not alter or modify the GX device software itself.

- This code is provided as is.
- The developer does not assume any liability for issues caused by the use of this integration.
- Use at your own risk.
