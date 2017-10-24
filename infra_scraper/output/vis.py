
import logging
from .base import BaseOutput
from infra_scraper.constants import get_icon

logger = logging.getLogger(__name__)


class VisOutput(BaseOutput):

    def __init__(self, **kwargs):
        super(VisOutput, self).__init__(**kwargs)

    def transform_data(self, data):
        resources = {}
        relations = []
        axes = {}
        i = 0
        kinds = len(data['resources'])
        for resource_name, resource_data in data['resources'].items():
            for resource_id, resource_item in resource_data.items():
                resource_item['kind'] = resource_item['kind'].replace(':', '_')
                resources[resource_id] = resource_item
            print data['resource_types'][resource_name]
            icon = get_icon(data['resource_types'][resource_name]['icon'])
            axes[resource_name] = {
                'x': i,
                'angle': 360 / kinds * i,
                'innerRadius': 0.2,
                'outerRadius': 1.0,
                'name': data['resource_types'][resource_name]['resource'],
                'items': len(data['resources'][resource_name]),
                'kind': resource_name,
                'icon': icon,
            }
            i += 1

        for relation_name, relation_data in data['relations'].items():
            for relation in relation_data:
                if relation['source'] in resources and relation['target'] in resources:
                    relations.append(relation)

        data['resources'] = resources
        data['relations'] = relations
        data['axes'] = axes
        return data
