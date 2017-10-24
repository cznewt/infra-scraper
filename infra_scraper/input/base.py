
import time
import logging

logger = logging.getLogger(__name__)


class BaseInput(object):

    def __init__(self, **kwargs):
        self.resources = {}
        self.resource_types = {}
        self.relations = {}
        self.timestamp = int(time.time())
        self._reverse_map = None

    def _create_relations(self):
        raise NotImplementedError

    def to_dict(self):
        self._create_relations()
        return {
            'name': self.name,
            'kind': self.kind,
            'timestamp': self.timestamp,
            'resource_types': self._get_resource_types(),
            'resources': self.resources,
            'relations': self.relations,
        }

    def _get_resource_types(self):
        resource_map = {}
        for resource_name, resource in self.resources.items():
            if resource_name in self.resources:
                resource_map[resource_name] = self.RESOURCE_MAP[resource_name]
        return resource_map

    def _get_resource_mapping(self):
        if self._reverse_map is None:
            self._reverse_map = {}
            for resource_name, resource in self.RESOURCE_MAP.items():
                self._reverse_map[resource['resource']] = resource_name
        return self._reverse_map

    def _scrape_resource(self, uid, name, kind, link=None, metadata={}):
        if kind not in self.resources:
            self.resources[kind] = {}
        self.resources[kind][uid] = {
            'id': uid,
            'kind': kind,
            'name': name,
            'metadata': metadata,
        }

    def _scrape_relation(self, kind, source, target):
        if kind not in self.relations:
            self.relations[kind] = []
        self.relations[kind].append({
            'source': source,
            'target': target,
        })
