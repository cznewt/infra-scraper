# -*- coding: utf-8 -*-

import os
import yaml
import tempfile
import os_client_config
from os_client_config import cloud_config
from heatclient.exc import HTTPBadRequest
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.openstack')


class OpenStackInput(BaseInput):

    def __init__(self, **kwargs):
        self.kind = 'openstack'
        self.scope = kwargs.get('scope', 'local')
        super(OpenStackInput, self).__init__(**kwargs)
        config_file, filename = tempfile.mkstemp()
        config_content = {
            'clouds': {self.name: self.config}
        }
        os.write(config_file, yaml.safe_dump(config_content).encode())
        os.close(config_file)
        self.cloud = os_client_config.config \
            .OpenStackConfig(config_files=[filename]) \
            .get_one_cloud(cloud=self.name)
        os.remove(filename)
        self.identity_api = self._get_client('identity')
        self.compute_api = self._get_client('compute')
        self.network_api = self._get_client('network')
        self.orch_api = self._get_client('orchestration')
        self.image_api = self._get_client('image')
        self.volume_api = self._get_client('volume')

    def _get_client(self, service_key):
        constructor = cloud_config._get_client(service_key)
        return self.cloud.get_legacy_client(service_key, constructor)

    def scrape_all_resources(self):
        if self.scope == 'global':
            self.scrape_keystone_projects()
#            self.scrape_keystone_users()
        self.scrape_cinder_volumes()
        self.scrape_glance_images()
        if self.scope == 'global':
            self.scrape_nova_aggregates()
            self.scrape_nova_hypervisors()
        self.scrape_nova_keypairs()
        self.scrape_nova_flavors()
        self.scrape_nova_servers()
#        self.scrape_nova_security_groups()
        self.scrape_neutron_networks()
        self.scrape_neutron_subnets()
        self.scrape_neutron_floating_ips()
        self.scrape_neutron_routers()
        self.scrape_neutron_ports()
        self.scrape_heat_stacks()
        # self.scrape_heat_resource_types()

    def _create_relations(self):
        # Define relationships between project and all namespaced resources.
        for resource_type, resource_dict in self.resources.items():
            for resource_id, resource in resource_dict.items():
                if 'tenant_id' in resource['metadata']:
                    self._scrape_relation(
                        'in_os_project',
                        resource_id,
                        resource['metadata']['tenant_id'])
                elif 'project' in resource['metadata']:
                    self._scrape_relation(
                        'in_os_project',
                        resource_id,
                        resource['metadata']['project'])

        for resource_id, resource in self.resources.get('os_stack', {}).items():
            for ext_res in resource['metadata']['resources']:
                if ext_res['resource_type'] in self._get_resource_mapping():
                    self._scrape_relation(
                        'os_stack-{}'.format(
                            self._get_resource_mapping()[ext_res['resource_type']]),
                        resource_id,
                        ext_res['physical_resource_id'])

        # Define relationships between aggregate zone and all hypervisors.
        for resource_id, resource in self.resources.get('os_aggregate', {}).items():
            for host in resource['metadata']['hosts']:
                self._scrape_relation(
                    'in_os_aggregate',
                    host,
                    resource_id)

        for resource_id, resource in self.resources.get('os_floating_ip', {}).items():
            if resource['metadata'].get('port_id', None) is not None:
                self._scrape_relation(
                    'use_os_port',
                    resource_id,
                    resource['metadata']['port_id'])

        for resource_id, resource in self.resources.get('os_port', {}).items():
            self._scrape_relation(
                'in_os_net',
                resource_id,
                resource['metadata']['network_id'])
            if resource['metadata']['device_id'] is not None:
                self._scrape_relation(
                    'use_os_port',
                    resource['metadata']['device_id'],
                    resource_id)
            if self.scope == 'global':
                if resource['metadata'].get('binding:host_id', False):
                    self._scrape_relation(
                        'on_os_hypervisor',
                        resource_id,
                        resource['metadata']['binding:host_id'])

        for resource_id, resource in self.resources.get('os_server', {}).items():
            if self.scope == 'global':
                self._scrape_relation(
                    'on_os_hypervisor',
                    resource_id,
                    resource['metadata']['OS-EXT-SRV-ATTR:host'])

            self._scrape_relation(
                'use_os_flavor',
                resource_id,
                resource['metadata']['flavor']['id'])

            if resource['metadata']['image'] != '':
                if resource['metadata']['image'].get('id', None) is not None:
                    self._scrape_relation(
                        'use_os_image',
                        resource_id,
                        resource['metadata']['image']['id'])

            if resource['metadata']['keypair_name'] != '':
                self._scrape_relation(
                    'use_os_key_pair',
                    resource_id,
                    resource['metadata']['keypair_name'])

        for resource_id, resource in self.resources.get('os_subnet', {}).items():
            self._scrape_relation(
                'in_os_net',
                resource_id,
                resource['metadata']['network_id'])

    def scrape_keystone_users(self):
        users = self.identity_api.get('/users')
        for user in users:
            resource = user.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_user', None, metadata=resource)

    def scrape_keystone_projects(self):
        projects = self.identity_api.tenants.list()
        for project in projects:
            resource = project.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_project', None, metadata=resource)

    def scrape_nova_aggregates(self):
        response = self.compute_api.aggregates.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['name'], resource['name'],
                                  'os_aggregate', None, metadata=resource)

    def scrape_nova_keypairs(self):
        response = self.compute_api.keypairs.list()
        for item in response:
            resource = item.to_dict()['keypair']
            self._scrape_resource(resource['name'],
                                  resource['name'],
                                  'os_key_pair', None, metadata=resource)

    def scrape_nova_flavors(self):
        response = self.compute_api.flavors.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'],
                                  resource['name'],
                                  'os_flavor', None, metadata=resource)

    def scrape_nova_hypervisors(self):
        response = self.compute_api.hypervisors.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['service']['host'],
                                  resource['hypervisor_hostname'],
                                  'os_hypervisor', None, metadata=resource)

    def scrape_nova_servers(self):
        if self.scope == 'global':
            search_opts = {'all_tenants': 1}
        else:
            search_opts = None
        response = self.compute_api.servers.list(
            search_opts=search_opts)
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_server', None, metadata=resource)

    def scrape_nova_security_groups(self):
        response = self.compute_api.security_groups.list(
            search_opts={'all_tenants': 1})
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_security_group', None, metadata=resource)

    def scrape_cinder_volumes(self):
        response = self.volume_api.volumes.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_volume', None, metadata=resource)

    def scrape_glance_images(self):
        response = self.image_api.images.list()
        for item in response:
            resource = item.__dict__['__original__']
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_image', None, metadata=resource)

    def scrape_neutron_routers(self):
        resources = self.network_api.list_routers().get('routers')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os_router', None, metadata=resource)

    def scrape_neutron_floating_ips(self):
        resources = self.network_api.list_floatingips().get('floatingips')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os_floating_ip', None, metadata=resource)

    def scrape_neutron_floating_ip_associations(self):
        resources = self.network_api.list_floatingips().get('floatingips')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os_floating_ip_association', None, metadata=resource)

    def scrape_neutron_networks(self):
        resources = self.network_api.list_networks().get('networks')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_net', None, metadata=resource)

    def scrape_neutron_subnets(self):
        resources = self.network_api.list_subnets().get('subnets')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_subnet', None, metadata=resource)

    def scrape_neutron_ports(self):
        resources = self.network_api.list_ports().get('ports')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_port', None, metadata=resource)

    # heat resources

    def scrape_heat_resource_types(self):
        resource_types = self.orch_api.resource_types.list(
            search_opts={'all_tenants': 1})
        for resource_type in resource_types:
            resource = resource_type.to_dict()
            self._scrape_resource(resource, resource,
                                  'os_resource_type', None, metadata=resource)

    def scrape_heat_stacks(self):
        if self.scope == 'global':
            search_opts = {'all_tenants': 1}
        else:
            search_opts = None
        stacks = self.orch_api.stacks.list(
            search_opts=search_opts)
        for stack in stacks:
            resource = stack.to_dict()
            resource['resources'] = []
            try:
                resources = self.orch_api.resources.list(stack.id,
                                                         nested_depth=2)
                for stack_resource in resources:
                    resource['resources'].append(stack_resource.to_dict())
            except HTTPBadRequest as exception:
                logger.error(exception)
            self._scrape_resource(resource['id'], resource['stack_name'],
                                  'os_stack', None, metadata=resource)
