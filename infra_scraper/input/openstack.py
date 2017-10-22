"""
https://docs.openstack.org/heat/latest/template_guide/openstack.html
"""

from heatclient.exc import HTTPBadRequest
import os_client_config
import logging
from .base import BaseInput

logger = logging.getLogger(__name__)


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
        self.orchestration_api = os_client_config.make_client(
            'orchestration', cloud=self.name)

    def scrape_all_resources(self):
        # keystone resources
#        self.scrape_users()
#        self.scrape_projects()
        # nova resources
        self.scrape_aggregates()
        self.scrape_flavors()
        self.scrape_hypervisors()
        self.scrape_servers()
        # neutron resources
        self.scrape_networks()
        self.scrape_subnets()
        self.scrape_floating_ips()
        self.scrape_routers()
        self.scrape_ports()
        # heat resources
        self.scrape_resource_types()
#        self.scrape_stacks()

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
        resource_types = self.orchestration_api.resource_types.list(
            search_opts={'all_tenants': 1})
        for resource_type in resource_types:
            resource = resource_type.to_dict()
            self._scrape_resource(resource, resource,
                                  'os:resource_type', None, metadata=resource)

    def scrape_stacks(self):
        stacks = self.orchestration_api.stacks.list(
            search_opts={'all_tenants': 1})
        for stack in stacks:
            resource = stack.to_dict()
            resource['resources'] = []
            try:
                stack_resources = self.orch_api.resources.list(stack.id,
                                                               nested_depth=2)
                for stack_resource in stack_resources:
                    resource['resources'].append(stack_resource.to_dict())
            except HTTPBadRequest as e:
                print e
            self._scrape_resource(resource['id'], resource['stack_name'],
                                  'os:stack', None, metadata=resource)
