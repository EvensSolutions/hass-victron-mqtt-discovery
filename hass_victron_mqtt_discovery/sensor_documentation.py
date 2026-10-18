from pyquery import PyQuery as pq

from .cache import Cache

class SensorDocumentation(Cache):

    def __init__(self, sensor_documentation_path):
        self.unit_device_class_map = {}
        self.unit_state_class_map = {}
        self.read_file(sensor_documentation_path)

    def read_file(self, path):
        cache_id = self.file_cache_id(path)
        page = pq(filename=path)

        self.read_device_classes(page, cache_id=cache_id)

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
