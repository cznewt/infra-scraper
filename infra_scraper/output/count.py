
import logging
from .base import BaseOutput

logger = logging.getLogger(__name__)


class CountOutput(BaseOutput):

    def __init__(self, **kwargs):
        super(CountOutput, self).__init__(**kwargs)

    def transform_data(self, data):
        resources = {}
        relations = {}

        for resource_name, resource_data in data['resources'].items():
            resources[resource_name] = len(resource_data)

        for relation_name, relation_data in data['relations'].items():
            relations[relation_name] = len(relation_data)

        data['resources'] = resources
        data['relations'] = relations
        data.pop('resource_types')
        return data
