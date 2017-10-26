# -*- coding: utf-8 -*-

from heatclient.exc import HTTPBadRequest
import os_client_config
import logging
from .base import BaseInput

logger = logging.getLogger(__name__)


class OpenStackInput(BaseInput):

    RESOURCE_MAP = {
        'os_aggregate': {
            'resource': 'Nova::Aggregate',
            'icon': 'fa:cube',
        },
        'os_flavor': {
            'resource': 'Nova::Flavor',
            'icon': 'fa:cube',
        },
        'os_floating_ip': {
            'resource': 'Neutron::FloatingIp',
            'icon': 'fa:cube',
        },
        'os_group': {
            'resource': 'Keystone::Group',
            'icon': 'fa:cube',
        },
        'os_hypervisor': {
            'resource': 'Nova::Hypervisor',
            'icon': 'fa:server',
        },
        'os_image': {
            'resource': 'Glance::Image',
            'icon': 'fa:cube',
        },
        'os_net': {
            'resource': 'Neutron::Net',
            'icon': 'fa:cube',
        },
        'os_port': {
            'resource': 'Neutron::Port',
            'icon': 'fa:cube',
        },
        'os_project': {
            'resource': 'Keystone::Tenant',
            'icon': 'fa:cube',
        },
        'os_resource_type': {
            'resource': 'Heat::ResourceType',
            'icon': 'fa:cube',
        },
        'os_router': {
            'resource': 'Neutron::Router',
            'icon': 'fa:cube',
        },
        'os_server': {
            'resource': 'Nova::Server',
            'icon': 'fa:cube',
        },
        'os_stack': {
            'resource': 'Heat::Stack',
            'icon': 'fa:cubes',
        },
        'os_subnet': {
            'resource': 'Neutron::Subnet',
            'icon': 'fa:cube',
        },
        'os_user': {
            'resource': 'Keystone::User',
            'icon': 'fa:cube',
        },
        'os_volume': {
            'resource': 'Cinder::Volume',
            'icon': 'fa:cube',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'openstack'
        super(OpenStackInput, self).__init__(**kwargs)

        try:
            self.name = kwargs['name']
        except KeyError:
            raise ValueError('Missing parameter name')

        self.scope = kwargs['scope']

        self.region = kwargs.get('region', 'RegionOne')
        self.identity_api = os_client_config.make_client(
            'identity', cloud=self.name)
        self.compute_api = os_client_config.make_client(
            'compute', cloud=self.name)
        self.network_api = os_client_config.make_client(
            'network', cloud=self.name)
        self.orch_api = os_client_config.make_client(
            'orchestration', cloud=self.name)
        self.image_api = os_client_config.make_client(
            'image', cloud=self.name)
        self.volume_api = os_client_config.make_client(
            'volume', cloud=self.name)

    def scrape_all_resources(self):
        # keystone resources
        # self.scrape_users()
        # self.scrape_projects()
        # cinder resources
        self.scrape_volumes()
        # glance resources
        # self.scrape_images()
        # nova resources
        if self.scope == 'global':
            self.scrape_aggregates()
        self.scrape_flavors()
        # self.scrape_security_groups()
        self.scrape_servers()
        if self.scope == 'global':
            self.scrape_hypervisors()
        # neutron resources
        self.scrape_networks()
        self.scrape_subnets()
        self.scrape_floating_ips()
        self.scrape_routers()
        self.scrape_ports()
        # heat resources
        self.scrape_resource_types()
        self.scrape_stacks()

    def _create_relations(self):
        # Define relationships between project and all namespaced resources.
        for resource_type, resource_dict in self.resources.items():
            for resource_id, resource in resource_dict.items():
                if 'tenant_id' in resource['metadata']:
                    self._scrape_relation(
                        '{}-os_project'.format(resource_type),
                        resource_id,
                        resource['metadata']['tenant_id'])
                elif 'project' in resource['metadata']:
                    self._scrape_relation(
                        '{}-os_project'.format(resource_type),
                        resource_id,
                        resource['metadata']['project'])

        for resource_id, resource in self.resources['os_stack'].items():
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
                    'os_hypervisor-os_aggregate',
                    host,
                    resource_id)

        for resource_id, resource in self.resources['os_port'].items():
            self._scrape_relation(
                'os_port-os_net',
                resource_id,
                resource['metadata']['network_id'])
            if resource['metadata']['device_id'] is not None:
                self._scrape_relation(
                    'os_port-os_server',
                    resource_id,
                    resource['metadata']['device_id'])
            if self.scope == 'global':
                if resource['metadata'].get('device_id', None) is not None:
                    self._scrape_relation(
                        'os_port-os_hypervisor',
                        resource_id,
                        resource['metadata']['binding:host_id'])

        for resource_id, resource in self.resources['os_server'].items():
            if self.scope == 'global':
                self._scrape_relation(
                    'os_server-os_hypervisor',
                    resource_id,
                    resource['metadata']['OS-EXT-SRV-ATTR:host'])

            self._scrape_relation(
                'os_server-os_flavor',
                resource_id,
                resource['metadata']['flavor']['id'])

            if resource['metadata']['image'] != '':
                if resource['metadata']['image'].get('id', None) is not None:
                    self._scrape_relation(
                        'os_server-os_image',
                        resource_id,
                        resource['metadata']['image']['id'])

        for resource_id, resource in self.resources['os_subnet'].items():
            self._scrape_relation(
                'os_subnet-os_net',
                resource_id,
                resource['metadata']['network_id'])

    # keystone resources

    def scrape_users(self):
        users = self.identity_api.get('/users')
        for user in users:
            resource = user.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_user', None, metadata=resource)

    def scrape_projects(self):
        projects = self.identity_api.tenants.list()
        for project in projects:
            resource = project.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_project', None, metadata=resource)

    # nova resources

    def scrape_aggregates(self):
        response = self.compute_api.aggregates.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['name'], resource['name'],
                                  'os_aggregate', None, metadata=resource)

    def scrape_flavors(self):
        response = self.compute_api.flavors.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'],
                                  resource['name'],
                                  'os_flavor', None, metadata=resource)

    def scrape_hypervisors(self):
        response = self.compute_api.hypervisors.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['service']['host'],
                                  resource['hypervisor_hostname'],
                                  'os_hypervisor', None, metadata=resource)

    def scrape_servers(self):
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

    def scrape_security_groups(self):
        response = self.compute_api.security_groups.list(
            search_opts={'all_tenants': 1})
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_security_group', None, metadata=resource)

    # cinder resources

    def scrape_volumes(self):
        response = self.volume_api.volumes.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_volume', None, metadata=resource)

    # glance resources

    def scrape_images(self):
        response = self.image_api.images.list()
        for item in response:
            print item.__class__
            resource = item.__class__
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_image', None, metadata=resource)

    # neutron resources

    def scrape_routers(self):
        resources = self.network_api.list_routers().get('routers')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os_router', None, metadata=resource)

    def scrape_floating_ips(self):
        resources = self.network_api.list_floatingips().get('floatingips')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os_floating_ip', None, metadata=resource)

    def scrape_networks(self):
        resources = self.network_api.list_networks().get('networks')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_net', None, metadata=resource)

    def scrape_subnets(self):
        resources = self.network_api.list_subnets().get('subnets')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_subnet', None, metadata=resource)

    def scrape_ports(self):
        resources = self.network_api.list_ports().get('ports')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os_port', None, metadata=resource)

    # heat resources

    def scrape_resource_types(self):
        resource_types = self.orch_api.resource_types.list(
            search_opts={'all_tenants': 1})
        for resource_type in resource_types:
            resource = resource_type.to_dict()
            self._scrape_resource(resource, resource,
                                  'os_resource_type', None, metadata=resource)

    def scrape_stacks(self):
        if self.scope == 'global':
            search_opts = {'all_tenants': 1}
        else:
            search_opts = None
        stacks = self.orch_api.stacks.list(
            search_opts=search_opts)
        i = 0
        for stack in stacks:
            if i < 2:
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
            i += 1
