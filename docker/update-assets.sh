#! /bin/sh

APP=${APP:-`pwd`}

mkdir -p $APP/assets
mkdir -p /tmp/assets/
cd /tmp/assets/

get_asset() {
    wget --quiet "$1" -O "$2"
    [ -s "$2" ] && mv "$2" $APP/assets/$2
}

get_asset "$ASSET_MODBUS_REGISTERS_URL" modbus-registers.xlsx
get_asset "$ASSET_SENSOR_DOCUMENTATION_URL" sensor-documentation.html
