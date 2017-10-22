
import logging

logger = logging.getLogger(__name__)


class BaseStorage(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.last_timestamp = None
