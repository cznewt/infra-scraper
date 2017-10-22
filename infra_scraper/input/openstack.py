"""
https://docs.openstack.org/heat/latest/template_guide/openstack.html
"""

from heatclient.exc import HTTPBadRequest
import os_client_config
import logging
from .base import BaseInput

logger = logging.getLogger(__name__)

OS_RES_MAPPING = {
    'OS::Nova::Server': 'os:server',
    'OS::Neutron::Port': 'os:port',
    'OS::Neutron::Subnet': 'os:subnet',
    'OS::Neutron::Net': 'os:network'
}


class OpenStackInput(BaseInput):

    def __init__(self, **kwargs):
        self.kind = 'openstack'
        super(OpenStackInput, self).__init__(**kwargs)

        try:
            self.name = kwargs['name']
        except KeyError:
            raise ValueError('Missing parameter name')

        self.region = kwargs.get('region', 'RegionOne')
        self.cloud = os_client_config.OpenStackConfig().get_one_cloud(
            self.name, self.region)

        self.identity_api = os_client_config.make_rest_client(
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
        self.scrape_aggregates()
        self.scrape_flavors()
        self.scrape_servers()
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
                        '{}-os:project'.format(resource_type),
                        resource_id,
                        resource['metadata']['tenant_id'])
                elif 'project' in resource['metadata']:
                    self._scrape_relation(
                        '{}-os:project'.format(resource_type),
                        resource_id,
                        resource['metadata']['project'])

        for resource_id, resource in self.resources['os:stack'].items():
            for ext_resource in resource['metadata']['resources']:
                if ext_resource['resource_type'] in OS_RES_MAPPING:
                    self._scrape_relation(
                        'os:stack-{}'.format(
                            OS_RES_MAPPING[ext_resource['resource_type']]),
                        resource_id,
                        ext_resource['physical_resource_id'])

        # Define relationships between aggregate zone and all hypervisors.
        for resource_id, resource in self.resources['os:aggregate'].items():
            for host in resource['metadata']['hosts']:
                self._scrape_relation(
                    'os:hypervisor-os:aggregate',
                    host,
                    resource_id)

        for resource_id, resource in self.resources['os:port'].items():
            self._scrape_relation(
                'os:port-os:network',
                resource_id,
                resource['metadata']['network_id'])
            if resource['metadata']['device_id'] is not None:
                self._scrape_relation(
                    'os:port-os:server',
                    resource_id,
                    resource['metadata']['device_id'])
            if resource['metadata'].get('device_id', None) is not None:
                self._scrape_relation(
                    'os:port-os:hypervisor',
                    resource_id,
                    resource['metadata']['binding:host_id'])

        for resource_id, resource in self.resources['os:server'].items():
            self._scrape_relation(
                'os:server-os:hypervisor',
                resource_id,
                resource['metadata']['OS-EXT-SRV-ATTR:host'])
            self._scrape_relation(
                'os:server-os:flavor',
                resource_id,
                resource['metadata']['flavor']['id'])

        for resource_id, resource in self.resources['os:subnet'].items():
            self._scrape_relation(
                'os:subnet-os:network',
                resource_id,
                resource['metadata']['network_id'])

    # keystone resources

    def scrape_users(self):
        users = self.identity_api.get('/users')
        for user in users:
            resource = user.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:user', None, metadata=resource)

    def scrape_projects(self):
        projects = self.identity_api.tenants.list()
        for project in projects:
            resource = project.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:project', None, metadata=resource)

    # nova resources

    def scrape_aggregates(self):
        response = self.compute_api.aggregates.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['name'], resource['name'],
                                  'os:aggregate', None, metadata=resource)

    def scrape_flavors(self):
        response = self.compute_api.flavors.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'],
                                  resource['name'],
                                  'os:flavor', None, metadata=resource)

    def scrape_hypervisors(self):
        response = self.compute_api.hypervisors.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['service']['host'],
                                  resource['hypervisor_hostname'],
                                  'os:hypervisor', None, metadata=resource)

    def scrape_servers(self):
        response = self.compute_api.servers.list(
            search_opts={'all_tenants': 1})
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:server', None, metadata=resource)

    # cinder resources

    def scrape_volumes(self):
        response = self.volume_api.volumes.list()
        for item in response:
            resource = item.to_dict()
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:volume', None, metadata=resource)

    # glance resources

    def scrape_images(self):
        response = self.image_api.images.list()
        for item in response:
            resource = item
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:image', None, metadata=resource)

    # neutron resources

    def scrape_routers(self):
        resources = self.network_api.list_routers().get('routers')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os:router', None, metadata=resource)

    def scrape_floating_ips(self):
        resources = self.network_api.list_floatingips().get('floatingips')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['id'],
                                  'os:floating_ip', None, metadata=resource)

    def scrape_networks(self):
        resources = self.network_api.list_networks().get('networks')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:network', None, metadata=resource)

    def scrape_subnets(self):
        resources = self.network_api.list_subnets().get('subnets')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:subnet', None, metadata=resource)

    def scrape_ports(self):
        resources = self.network_api.list_ports().get('ports')
        for resource in resources:
            self._scrape_resource(resource['id'], resource['name'],
                                  'os:port', None, metadata=resource)

    # heat resources

    def scrape_resource_types(self):
        resource_types = self.orch_api.resource_types.list(
            search_opts={'all_tenants': 1})
        for resource_type in resource_types:
            resource = resource_type.to_dict()
            self._scrape_resource(resource, resource,
                                  'os:resource_type', None, metadata=resource)

    def scrape_stacks(self):
        stacks = self.orch_api.stacks.list(
            search_opts={'all_tenants': 1})
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
                                      'os:stack', None, metadata=resource)
            i += 1
