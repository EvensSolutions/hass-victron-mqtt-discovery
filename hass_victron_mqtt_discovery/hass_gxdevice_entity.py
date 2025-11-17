import re
import json

from functools import cached_property

from .topic_components import TopicComponents

RE_OPTIONS = r'((\d+)=[^;]+;\s*)*((\d+)=[^;]+)'

class HomeAssistantGXDeviceEntity:

    def __init__(self, gx_device, register, topic, payload={}):
        self.topic = topic
        self.payload = payload
        self.register = register
        self.entity_config = {}
        self.gx_device = gx_device

    @property
    def sensor_documentation(self):
        return self.gx_device.sensor_documentation

    @cached_property
    def is_enum(self):
        if self.register['unit'] is None:
            return False

        return re.match(RE_OPTIONS, self.register['unit'])

    @cached_property
    def is_writable(self):
        return self.register['writable']

    @cached_property
    def value(self):
        return self.payload['value']

    @cached_property
    def topic_components(self):
        return TopicComponents.from_topic(self.topic)

    @cached_property
    def device_id(self):
        c = self.topic_components

        return "%s_%s_%s" % (c.serial, c.service, c.instance)

    @cached_property
    def topic_id(self):
        return self.topic_components.dbus_topic[1:].replace('/', '_')

    @cached_property
    def unit(self):
        unit = self.register['unit']

        if unit is None or unit == 'count' or self.is_enum:
            return None

        unit = re.sub(r'^(A|V) (AC|DC)$', '\\1', unit)
        unit = unit.replace('Degrees celsius', '°C')
        unit = unit.replace('Degrees fahrenheit', '°F')
        unit = unit.replace('seconds', 's')
        unit = unit.split(' or ')[-1].strip()
        unit = re.sub(r'^watts?$', 'W', unit, flags=re.I)

        return unit

    @cached_property
    def options(self):
        if not self.is_enum:
            return None

        matches = re.findall(r'(\d+)=([^;]+)', self.register['unit'])
        maxIndex = max([ int(v[0]) for v in matches ]) + 1
        options = [None] * maxIndex
        for [ key, value ] in matches:
            options[int(key)] = value

        return options

    @cached_property
    def device_class(self):
        if self.is_enum:
            return 'enum';

        device_class = self.sensor_documentation.device_class_from_unit(self.unit)
        if device_class is not None:
            return device_class

        return None

    @cached_property
    def state_class(self):
        unit = self.unit
        sensor_state_class = self.sensor_documentation.state_class_from_unit(unit)

        if sensor_state_class is not None:
            return sensor_state_class

        return None

    @cached_property
    def device_type(self):
        default = 'sensor'

        if not self.is_writable:
            return default

        if self.is_enum:
            return 'select'

        value_type = self.register['type']

        if re.match(r'u?int(32|16)', value_type):
            return 'number'

        if re.match(r'string', value_type):
            return 'text'

        return default

    @cached_property
    def entity_info(self):
        info = {}

        if self.device_class is not None:
            info['device_class'] = self.device_class

        if self.state_class is not None:
            info['state_class'] = self.state_class

        if self.options is not None:
            info['options'] = list(filter(None, self.options))

        if isinstance(self.value, float):
            scalefactor = self.register['scalefactor']
            info['suggested_display_precision'] = max([ len(str(scalefactor)) -1, 0 ])

        if not self.is_writable:
            return info

        if self.device_type == 'number':
            info['mode'] = 'box'
            info['max'] = 2^31 - 1;
            info['min'] = -2^31

            value_range = self.register.get('range', None)
            if value_range is not None:
                info['max'] = max(value_range)
                info['min'] = min(value_range)

            if 'max' in self.payload: info['max'] = self.payload['max']
            if 'min' in self.payload: info['min'] = self.payload['min']

        if self.device_type != 'sensor':
            info['command_topic'] = re.sub(r'(^|/)N/', r'\1W/', self.topic)
            info['command_template'] = '{{ { "value": value } | tojson }}'

        if self.is_enum:
            # Swap keys and value to map text values to numeric equivalent
            options = { v: k for k, v in enumerate(self.options) if v is not None }
            template = json.dumps(options) + '[value]'
            info['command_template'] = '{{ { "value": %s } | tojson }}' % template

        return info

    @cached_property
    def device_description(self):
        c = self.topic_components

        return {
            'name': 'Victron %s %s #%s' % (c.serial, c.service, c.instance),
            'manufacturer': 'Victron Energy',
            'serial_number': c.serial,
            'identifiers': [ self.device_id ]
        }

    @cached_property
    def name(self):
        name = self.register['name']
        name = re.sub(r'System;\s*', '', name)
        return name[0].upper() + name[1:]

    @cached_property
    def value_template(self):
        value_template = 'value_json.value'

        if self.device_class == 'enum':
            value_template = json.dumps(self.options) + '[value_json.value]'

        return "{{ %s }}" % value_template

    @cached_property
    def entity_description(self):
        return {
            **self.entity_info,
            'name': self.name,
            'unique_id': '%s:%s' % (self.device_id, self.topic_id),
            'state_topic': self.topic,
            'value_template': self.value_template,
            'unit_of_measurement': self.unit,
            'device': self.device_description,
            'enabled_by_default': self.value is not None,
        }
