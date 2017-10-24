
from .base import BaseStorage
import os
import etcd
import yaml
import logging

logger = logging.getLogger(__name__)


class EtcdStorage(BaseStorage):

    def __init__(self, **kwargs):
        super(EtcdStorage, self).__init__(**kwargs)
        self.client = etcd.Client(
            host='127.0.0.1', port=4003)
        self.storage_path = '/scrape'

    def _get_storage_path(self, name):
        return os.path.join(self.storage_path, self.name)

    def save_data(self, name, data):
        filename = os.path.join(self._get_storage_path(),
                                data['timestamp'])
        with open(filename, 'w') as outfile:
            yaml.safe_dump(data, outfile, default_flow_style=False)
        self.last_timestamp = data['timestamp']

    def load_data(self, name):
        data = None
        if self.last_timestamp is not None:
            filename = '{}/{}.yaml'.format(self._get_storage_path(),
                                           self.last_timestamp)
            with open(filename, 'r') as stream:
                try:
                    data = yaml.load(stream)
                except yaml.YAMLError as exception:
                    logger.error(exception)
        return data
