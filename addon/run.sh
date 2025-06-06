#!/usr/bin/with-contenv bashio

bashio::log.info "Loading python environment"
. /app/bin/activate

bashio::log.info "Setting up configuration"
export MQTT_HOST=$(bashio::config 'mqtt_host')
export MQTT_HOST=${MQTT_HOST:-$(bashio::services mqtt "host")}

export MQTT_PORT=$(bashio::config 'mqtt_port')
export MQTT_PORT=${MQTT_PORT:-$(bashio::services mqtt "port")}

export MQTT_USERNAME=$(bashio::config 'mqtt_username')
export MQTT_USERNAME=${MQTT_USERNAME:-$(bashio::services mqtt "username")}

export MQTT_PASSWORD=$(bashio::config 'mqtt_password')
export MQTT_PASSWORD=${MQTT_PASSWORD:-$(bashio::services mqtt "password")}

export ASSET_MODBUS_REGISTERS_URL=$(bashio::config 'asset_modbus_registers_url')
export ASSET_SENSOR_DOCUMENTATION_URL=$(bashio::config 'asset_sensor_documentation_url')

bashio::log.info "Starting discovery"
exec ./docker-entrypoint.sh < /dev/null
