
import logging
from .base import BaseOutput
from datetime import datetime
from infra_scraper.utils import get_node_icon

logger = logging.getLogger(__name__)


class VisOutput(BaseOutput):

    def __init__(self, **kwargs):
        super(VisOutput, self).__init__(**kwargs)

    def _transform_openstack(self, data):
        resources = {}
        relations = []
        axes = {}
        i = 0
        kinds = 0
        for resource_name, resource_data in data['resources'].items():
            if resource_name != 'os_port':
                kinds += 1

        for resource_name, resource_data in data['resources'].items():
            if resource_name != 'os_port':
                for resource_id, resource_item in resource_data.items():
                    resource_item.pop('metadata')
                    resources[resource_id] = resource_item
                icon = get_node_icon(data['resource_types'][resource_name]['icon'])
                axes[resource_name] = {
                    'x': i,
                    'angle': 360 / kinds * i,
                    'innerRadius': 0.2,
                    'outerRadius': 1.0,
                    'name': data['resource_types'][resource_name]['name'],
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

    def _transform_default(self, data):
        resources = {}
        relations = []
        axes = {}
        i = 0
        kinds = len(data['resources'])
        for resource_name, resource_data in data['resources'].items():
            for resource_id, resource_item in resource_data.items():
                resource_item.pop('metadata')
                resources[resource_id] = resource_item
            icon = get_node_icon(data['resource_types'][resource_name]['icon'])
            axes[resource_name] = {
                'x': i,
                'angle': 360 / kinds * i,
                'innerRadius': 0.2,
                'outerRadius': 1.0,
                'name': data['resource_types'][resource_name]['name'],
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

    def transform_data(self, data):
        data['date'] = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')
        if data['kind'] == 'openstack':
            return self._transform_openstack(data)
        else:
            return self._transform_default(data)


class VisHierOutput(BaseOutput):

    def __init__(self, **kwargs):
        super(VisHierOutput, self).__init__(**kwargs)

    def _transform_openstack(self, data):
        resources = {}
        out_resources = []

        for resource_name, resource_data in resources.items():
            out_resources.append({
                'name': resource_name,
                'size': 1,
                'relations': resource_data['relations']
            })
        data['resources'] = out_resources
        data.pop('relations')
        data.pop('resource_types')
        return data

    def _transform_default(self, data):
        resources = {}
        out_resources = []

        for resource_name, resource_data in data['resources'].items():
            if resource_name == 'salt_service':
                for resource_id, resource_item in resource_data.items():
                    resource_item['relations'] = []
                    resources['root|{}'.format(resource_id)] = resource_item

        for relation_name, relation_data in data['relations'].items():
            if relation_name == 'salt_service-salt_service':

                for relation in relation_data:
                    relation['source'] = 'root|{}'.format(relation['source'])
                    relation['target'] = 'root|{}'.format(relation['target'])
                    resources[relation['source']]['relations'].append(
                        relation['target'])

        for resource_name, resource_data in resources.items():
            out_resources.append({
                'name': resource_name,
                'size': 1,
                'relations': resource_data['relations']
            })
        data['resources'] = out_resources
        data.pop('relations')
        data.pop('resource_types')
        return data

    def transform_data(self, data):
        data['date'] = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')
        if data['kind'] == 'openstack':
            return self._transform_openstack(data)
        else:
            return self._transform_default(data)
