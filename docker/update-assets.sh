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

# The sensor documentation links to the file that defines DEVICE_CLASS_STATE_CLASSES
SENSOR_CONST_URL=`grep -o 'DEVICE_CLASS_STATE_CLASSES</code> in <a href="[^"]*"' $APP/assets/sensor-documentation.html | head -n 1 \
    | sed -e 's/.*href="//' -e 's/"$//' -e 's#github\.com/\([^/]*/[^/]*\)/blob/#raw.githubusercontent.com/\1/#'`

[ -n "$SENSOR_CONST_URL" ] && get_asset "$SENSOR_CONST_URL" sensor-const.py
