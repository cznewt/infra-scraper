
import logging
from .base import BaseOutput

logger = logging.getLogger(__name__)


class CountOutput(BaseOutput):

    def __init__(self, **kwargs):
        super(CountOutput, self).__init__(**kwargs)

    def transform_data(self, data):
        output = {}
        for resource_name, resource_data in data['resources'].items():
            output[resource_name] = len(resource_data)

        return output
