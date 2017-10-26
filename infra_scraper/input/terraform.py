# -*- coding: utf-8 -*-

import logging
from .base import BaseInput

logger = logging.getLogger(__name__)


class TerraformInput(BaseInput):

    RESOURCE_MAP = {
        'tf_resource': {
            'resource': 'Resource',
            'icon': 'fa:cube',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'openstack'
        super(TerraformInput, self).__init__(**kwargs)

        try:
            self.name = kwargs['name']
        except KeyError:
            raise ValueError('Missing parameter name')

    def scrape_all_resources(self):
        self.scrape_resources()

    def _create_relations(self):
        # Define relationships between project and all namespaced resources.
        pass

    def scrape_resources(self):
        resource_types = self.orch_api.resource_types.list(
            search_opts={'all_tenants': 1})
        for resource_type in resource_types:
            resource = resource_type.to_dict()
            self._scrape_resource(resource, resource,
                                  'os_resource_type', None, metadata=resource)
