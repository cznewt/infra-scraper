
import logging
from .base import BaseOutput

logger = logging.getLogger(__name__)


class RawOutput(BaseOutput):

    def __init__(self, **kwargs):
        super(RawOutput, self).__init__(**kwargs)

    def transform_data(self, data):
        resources = {}

        for resource_name, resource_data in data['resources'].items():
            resources[resource_name] = []
            for resource_id, resource_item in resource_data.items():
                resources[resource_name].append(resource_item['metadata'])

        data['resources'] = resources
        return data
