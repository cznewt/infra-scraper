
import logging

logger = logging.getLogger(__name__)


class BaseStorage(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.last_timestamp = None

    def save_data(self, name, data):
        raise NotImplementedError

    def load_data(self, name):
        raise NotImplementedError

    def save_output_data(self, name, kind, data):
        raise NotImplementedError

    def load_output_data(self, name, kind):
        raise NotImplementedError
