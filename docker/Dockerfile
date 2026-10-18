FROM python:3-alpine

RUN mkdir -p /app
WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD hass_victron_mqtt_discovery hass_victron_mqtt_discovery
ADD docker/*.sh .

ENV ASSET_MODBUS_REGISTERS_URL="https://www.victronenergy.com/upload/documents/CCGX-Modbus-TCP-register-list-3.50.xlsx"
ENV ASSET_SENSOR_DOCUMENTATION_URL="https://contributors.home-assistant.io/core/entities/sensor/"

RUN ./update-assets.sh

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]
