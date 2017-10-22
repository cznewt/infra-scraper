
from .base import BaseStorage
import os
import yaml
import logging

logger = logging.getLogger(__name__)


class FileStorage(BaseStorage):

    def __init__(self, **kwargs):
        super(FileStorage, self).__init__(**kwargs)
        self.storage_dir = kwargs.get('storage_dir', '/tmp/scraper')
        try:
            os.stat(self.storage_dir)
        except Exception:
            os.mkdir(self.storage_dir)

    def _storage_dir_exist(self):
        try:
            os.stat(self._get_storage_dir())
        except Exception:
            os.mkdir(self._get_storage_dir())

    def _get_storage_dir(self):
        return os.path.join(self.storage_dir, self.name)

    def save_data(self, name, data):
        self.name = name
        self._storage_dir_exist()
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
