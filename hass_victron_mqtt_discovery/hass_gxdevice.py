import re
import json
import uuid
import asyncio
from datetime import datetime

from .utils import logger
from .topic_components import TopicComponents
from .hass_gxdevice_entity import HomeAssistantGXDeviceEntity

RESYNC_TTL = 3600

class HomeAssistantGXDevice:

    def __init__(self, mqtt_client, mqtt_prefix, serial, registers, sensor_documentation):
        self.mqtt = mqtt_client
        self.serial = serial
        self.registers = registers
        self.mqtt_prefix = re.sub(r'/+$', '', mqtt_prefix)
        self.sensor_documentation = sensor_documentation
        self.keepalive_id = str(uuid.uuid4())

    @property
    def keepalive_address(self):
        return '%s/R/%s/keepalive' % (self.mqtt_prefix, self.serial)

    async def resync(self, notify_complete=False):
        logger.info('Resyncing: %s' % self.keepalive_id)

        payload = { "keepalive-options" : [] }

        if notify_complete:
            payload['keepalive-options'].append({
                "full-publish-completed-echo": self.keepalive_id
            })

        await self.mqtt.publish(self.keepalive_address, json.dumps(payload))

    async def keepalive(self):
        await self.resync(notify_complete=True)

        keepalive = json.dumps({
            "keepalive-options" : [ "suppress-republish" ]
        })

        last_full_sync = datetime.now()

        while True:
            await asyncio.sleep(30)

            seconds_since_full_sync = (datetime.now() - last_full_sync).seconds
            if seconds_since_full_sync >= RESYNC_TTL:
                last_full_sync = datetime.now()
                await self.resync()
            else:
                await self.mqtt.publish(self.keepalive_address, keepalive)

    async def subscribe(self):
        asyncio.get_running_loop().create_task(self.keepalive())

    async def on_publish_completed(self, topic, payload):
        if 'full-publish-completed-echo' not in payload:
            return

        if payload['full-publish-completed-echo'] != self.keepalive_id:
            return

        await asyncio.sleep(2)
        await self.resync()

    async def on_mqtt_message(self, topic, payload):
        topic_components = TopicComponents.from_topic(topic)

        if not topic_components.valid:
            return

        if topic_components.serial != self.serial:
            return

        register = self.registers.lookup_mqtt_topic(topic)
        if register is None:
            return

        entity = HomeAssistantGXDeviceEntity(self, register, topic, payload=payload)

        await self.mqtt.publish(
            'homeassistant/%s/%s/%s/config' % (entity.device_type, entity.device_id, entity.topic_id),
            payload=json.dumps(entity.entity_description)
        )



