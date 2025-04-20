#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 jorgen <jorgen@jorgen-laptop>
#
# Distributed under terms of the MIT license.

import traceback
import aiomqtt
import asyncio
import json
import re

from .modbus_registers import ModbusRegisters
from .hass_gxdevice import HomeAssistantGXDevice
from .topic_components import TopicComponents
from .sensor_documentation import SensorDocumentation

RE_SERIAL = r'N/[^/]+/system/\d+/Serial$'
RE_PUBLISH_COMPLETE = r'N/([^/]+)/full_publish_completed$'

class HassVictronMqttDiscovery:

    def __init__(self,
        mqtt_host='127.0.0.1',
        mqtt_port=1883,
        mqtt_prefix="",
        registers=None,
        registers_path=None,
        sensor_documentation=None,
        sensor_documentation_path=None):

        self.task = None
        self.mqtt = None
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_prefix = mqtt_prefix

        self.devices = {}

        self.registers = self.init_registers(registers, registers_path)
        self.sensor_documentation = self.init_sensor_documentation(sensor_documentation, sensor_documentation_path)

    async def loop(self):
        if self.mqtt is not None:
            raise 'Discovery already started'

        self.mqtt = client = aiomqtt.Client(self.mqtt_host, self.mqtt_port)

        while self.mqtt is not None:
            try:
                async with self.mqtt:
                    await client.subscribe(self.mqtt_prefix + '#')
                    async for message in client.messages:
                        await self.on_message(message)
            except aiomqtt.MqttError:
                await asyncio.sleep(5)

        self.mqtt = None

    async def start(self):
        loop = asyncio.get_running_loop()
        self.task = loop.create_task(self.loop())
        await self.task

    def stop(self):
        self.mqtt = None
        self.task.cancel()

    def init_registers(self, registers, registers_path):
        if registers is not None:
            return registers

        if registers_path is not None:
            return ModbusRegisters(registers_path)

        raise 'Must supply either registers or registers_path'

    def init_sensor_documentation(self, sensor_documentation, sensor_documentation_path):
        if sensor_documentation is not None:
            return sensor_documentation

        if sensor_documentation_path is not None:
            return SensorDocumentation(sensor_documentation_path)

        raise 'Must supply either sensor_documentation or sensor_documentation_path'

    async def on_device_discovery(self, topic, payload):
        serial = payload['value']

        if serial not in self.devices:
            prefix = re.sub(RE_SERIAL, '', topic)
            print('Found device with serial "%s" at prefix "%s"' % (serial, prefix))
            self.devices[serial] = HomeAssistantGXDevice(self.mqtt, prefix, serial, self.registers, self.sensor_documentation)
            await self.devices[serial].subscribe()

    async def on_message(self, msg):
        try:
            topic = msg.topic.value
            payload = json.loads(msg.payload)

            if re.search(RE_SERIAL, topic) is not None:
                await self.on_device_discovery(topic, payload)

            publish_complete = re.search(RE_PUBLISH_COMPLETE, topic)
            if publish_complete is not None and publish_complete.group(1) in self.devices:
                serial = publish_complete.group(1)
                await self.devices[serial].on_publish_completed(topic, payload)

            c = TopicComponents.from_topic(topic)

            if c.serial in self.devices:
                await self.devices[c.serial].on_mqtt_message(topic, payload)
        except json.decoder.JSONDecodeError:
            # Ignore this error, the topic is not a valid victron topic
            pass
        except Exception as e:
            traceback.print_exception(e)
