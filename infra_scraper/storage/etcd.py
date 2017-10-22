
from .base import BaseStorage
import os
import yaml
import logging

logger = logging.getLogger(__name__)


class EtcdStorage(BaseStorage):

    def __init__(self, **kwargs):
        super(EtcdStorage, self).__init__(**kwargs)
        self.client = etcd.Client(
            host='127.0.0.1', port=4003)
        try:
            os.stat(self._get_storage_dir())
        except Exception:
            os. mkdir(self._get_storage_dir())

    def _get_storage_dir(self):
        return os.path.join(self.storage_dir, self.name)

    def save_data(self, name, data):
        filename = '{}/{}.yaml'.format(self._get_storage_dir(),
                                       data['timestamp'])
        with open(filename, 'w') as outfile:
            yaml.safe_dump(data, outfile, default_flow_style=False)
        self.last_timestamp = data['timestamp']

    def load_data(self, name):
        data = None
        if self.last_timestamp is not None:
            filename = '{}/{}.yaml'.format(self._get_storage_dir(),
                                           self.last_timestamp)
            with open(filename, 'r') as stream:
                try:
                    data = yaml.load(stream)
                except yaml.YAMLError as exception:
                    logger.error(exception)
        return data
