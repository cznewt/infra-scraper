
import time
import logging

logger = logging.getLogger(__name__)


class BaseInput(object):

    def __init__(self, **kwargs):
        self.resources = {}
        self.counters = {}
        self.timestamp = int(time.time())

    def to_dict(self):
        return {
            'name': self.name,
            'kind': self.kind,
            'timestamp': self.timestamp,
            'resources': self.resources,
        }

    def _scrape_resource(self, uid, name, kind, link=None, metadata={}):
        if kind not in self.resources:
            self.resources[kind] = {}
            self.counters[kind] = 1
        else:
            if uid not in self.resources[kind]:
                self.counters[kind] += 1
        self.resources[kind][uid] = {
            'id': uid,
            'kind': kind,
            'name': name,
            'metadata': metadata,
        }
