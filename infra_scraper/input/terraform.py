# -*- coding: utf-8 -*-

import python_terraform
from graphviz import Digraph
import logging
import StringIO

from .base import BaseInput

logger = logging.getLogger(__name__)


class TerraformInput(BaseInput):

    RESOURCE_MAP = {
        'tf_openstack_compute_instance_v2': {
            'resource': 'Compute',
            'icon': 'fa:server',
        },
        'tf_openstack_compute_keypair_v2': {
            'resource': 'KeyPair',
            'icon': 'fa:cube',
        },
        'tf_openstack_compute_secgroup_v2': {
            'resource': 'SecGroup',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_router_interface_v2': {
            'resource': 'RouterInterface',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_router_v2': {
            'resource': 'Router',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_network_v2': {
            'resource': 'Subnet',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_subnet_v2': {
            'resource': 'Subnet',
            'icon': 'fa:cube',
        },
        'tf_openstack_networking_floatingip_v2': {
            'resource': 'Subnet',
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
        print self.client.fmt(diff=True)

    def scrape_all_resources(self):
        self.scrape_resources()

    def _create_relations(self):
        return_code, raw_data, stderr = self.client.graph()

    def scrape_resources(self):
        res = None
        return_code, raw_data, stderr = self.client.show()
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
                resource_id = line.replace(' (tainted', '').replace(' (:', '')
                try:
                    resource_kind, resource_name = resource_id.split('.')
                    if resource_kind == '\x1b[0mopenstack_compute_instance_v2':
                        resource_kind = 'openstack_compute_instance_v2'
                    res = {
                        'id': resource_id,
                        'name': resource_name,
                        'kind': 'tf_{}'.format(resource_kind),
                        'metadata': {}
                    }
                except Exception:
                    pass
