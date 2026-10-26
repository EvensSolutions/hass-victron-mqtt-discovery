import re

from pyquery import PyQuery as pq

from .cache import Cache

class SensorDocumentation(Cache):

    def __init__(self, sensor_documentation_path, sensor_const_path=None):
        self.unit_device_class_map = {}
        self.unit_state_class_map = {}
        self.device_class_state_classes = {}
        self.read_file(sensor_documentation_path)

        if sensor_const_path is not None:
            self.read_const_file(sensor_const_path)

    def read_file(self, path):
        cache_id = self.file_cache_id(path)
        page = pq(filename=path)

        self.read_device_classes(page, cache_id=cache_id)

    def read_const_file(self, path):
        cache_id = self.file_cache_id(path)
        cache_item = self.load_cache(cache_id, None)

        if not isinstance(cache_item, dict):
            with open(path, 'r') as f:
                cache_item = self.parse_device_class_state_classes(f.read())
            self.update_cache(cache_id, cache_item)

        self.device_class_state_classes = cache_item

    @staticmethod
    def parse_device_class_state_classes(source):
        """Read DEVICE_CLASS_STATE_CLASSES from Home Assistant's sensor/const.py."""
        all_classes = re.findall(r'^    ([A-Z_]+) = ', re.search(r'class SensorStateClass.*?\n\n\n', source, re.S)[0], re.M)
        block = re.search(r'DEVICE_CLASS_STATE_CLASSES.*?\n}', source, re.S)[0]

        result = {}

        for device_class, classes in re.findall(r'SensorDeviceClass\.(\w+):\s*(set\([^)]*\)|{[^}]*})', block):
            names = all_classes if 'SensorStateClass)' in classes else re.findall(r'SensorStateClass\.(\w+)', classes)
            result[device_class.lower()] = [ n.lower() for n in names ]

        return result

    def valid_state_class(self, device_class, state_class):
        """Return a state class Home Assistant accepts for the device class."""
        allowed = self.device_class_state_classes.get(device_class)

        if state_class is None or allowed is None or state_class in allowed:
            return state_class

        # Prefer a cumulative class that handles resets (e.g. "yield today")
        return 'total_increasing' if 'total_increasing' in allowed else next(iter(allowed), None)

    def add_unit_device_class_mapping(self, unit, clazz):
        if unit in self.unit_device_class_map:
            return

        self.unit_device_class_map[unit] = clazz

    def add_unit_state_class_mapping(self, unit, state_class):
        if unit in self.unit_state_class_map:
            return

        self.unit_state_class_map[unit] = state_class

    def read_device_classes(self, page, cache_id=None):
        if cache_id is not None and self.has_cache(cache_id):
            cache_item = self.load_cache(cache_id)

            if isinstance(cache_item, list):
                self.unit_device_class_map, self.unit_state_class_map = cache_item
                return

        heading = page('#device-classes').parent()
        state_table = next(
            pq(table) for table in heading.next_all('table').items()
            if len(pq(table)('tbody tr').eq(0)('td')) == 3
        )

        for row in state_table('tbody tr').items():
            clazz, units, description = [ pq(c).text() for c in row('td') ]
            clazz = clazz.split('.')[-1].lower()
            units = [ u.strip() for u in units.split(',') ]

            for u in units:
                self.add_unit_device_class_mapping(u, clazz)
                self.add_unit_state_class_mapping(u, 'total' if 'over time' in description else 'measurement')

        if cache_id is not None:
            self.update_cache(cache_id, [
                self.unit_device_class_map,
                self.unit_state_class_map,
            ])

    def state_class_from_unit(self, unit):
        if unit in self.unit_state_class_map:
            return self.unit_state_class_map[unit]

        return None

    def device_class_from_unit(self, unit):
        if unit in self.unit_device_class_map:
            return self.unit_device_class_map[unit]

        return None
