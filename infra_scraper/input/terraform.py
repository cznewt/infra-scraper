# -*- coding: utf-8 -*-

import StringIO
import python_terraform
from pydot import graph_from_dot_data
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.terraform')


class TerraformInput(BaseInput):

    RESOURCE_MAP = {
        'tf_openstack_compute_instance_v2': {
            'resource': 'openstack_compute_instance_v2',
            'name': 'Instance',
            'icon': 'fa:server',
        },
        'tf_openstack_compute_keypair_v2': {
            'resource': 'openstack_compute_keypair_v2',
            'name': 'Key Pair',
            'icon': 'fa:cube',
        },
        'tf_openstack_compute_secgroup_v2': {
            'resource': 'openstack_compute_secgroup_v2',
            'name': 'Security Group',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_router_interface_v2': {
            'resource': 'openstack_networking_router_interface_v2',
            'name': 'Router Interface',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_router_v2': {
            'resource': 'openstack_networking_router_v2',
            'name': 'Router',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_network_v2': {
            'resource': 'openstack_networking_network_v2',
            'name': 'Net',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_subnet_v2': {
            'resource': 'openstack_networking_subnet_v2',
            'name': 'Subnet',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_floatingip_v2': {
            'resource': 'openstack_networking_floatingip_v2',
            'name': 'Floating IP',
            'icon': 'fa:cube',
        },
        'tf_openstack_compute_floatingip_associate_v2': {
            'resource': 'openstack_compute_floatingip_associate_v2',
            'name': 'Floating IP Association',
            'icon': 'fa:cube',
        },
    }

    def __init__(self, **kwargs):
        super(TerraformInput, self).__init__(**kwargs)
        self.kind = 'terraform'
        self.name = kwargs['name']

        try:
            self.config_dir = kwargs['config_dir']
        except KeyError:
            raise ValueError('Missing parameter config_dir')

        self.client = python_terraform.Terraform(working_dir=self.config_dir)

    def scrape_all_resources(self):
        self.scrape_resources()

    def clean_name(self, name):
        return name.replace('"', '').replace('[root] ', '').strip()

    def _create_relations(self):
        return_code, raw_data, stderr = self.client.graph(no_color=python_terraform.IsFlagged)
        graph = graph_from_dot_data(raw_data)[0]
        for node in graph.obj_dict['subgraphs']['"root"'][0]['nodes']:
            print node
        for edge in graph.obj_dict['subgraphs']['"root"'][0]['edges']:
            source = self.clean_name(edge[0]).split('.')
            target = self.clean_name(edge[1]).split('.')
            if 'tf_{}'.format(source[0]) in self.resources and 'tf_{}'.format(target[0]) in self.resources:
                self._scrape_relation(
                    'tf_{}-tf_{}'.format(source[0], target[0]),
                    '{}.{}'.format(source[0], source[1]),
                    '{}.{}'.format(target[0], target[1]))

    def scrape_resources(self):
        res = None
        return_code, raw_data, stderr = self.client.show(no_color=python_terraform.IsFlagged)
        raw_data = raw_data.split('Outputs:')[0]
        data_buffer = StringIO.StringIO(raw_data)
        for line in data_buffer.readlines():
            if line.strip() == '':
                pass
            elif line.startswith('  '):
                meta_key, meta_value = line.split(' = ')
                res['metadata'][meta_key.strip()] = meta_value.strip()
            else:
                if res is not None:
                    self._scrape_resource(res['id'], res['name'],
                                          res['kind'], None,
                                          metadata=res['metadata'])
                resource_id = line.replace(' (tainted', '') \
                    .replace(':', '').replace('(', '').replace(')', '').strip()
                try:
                    resource_kind, resource_name = str(resource_id).split('.')
                    res = {
                        'id': resource_id,
                        'name': resource_name.strip(),
                        'kind': 'tf_{}'.format(resource_kind),
                        'metadata': {}
                    }
                except Exception as exception:
                    print exception
