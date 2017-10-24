# -*- coding: utf-8 -*-

import logging
from .base import BaseInput
from infra_scraper.utils import load_yaml_json_file
from pepper.libpepper import Pepper
logger = logging.getLogger(__name__)


class SaltStackInput(BaseInput):

    RESOURCE_MAP = {
        'salt_high_state': {
            'resource': 'High State',
            'icon_set': 'FontAwesome',
            'icon_char': 'f233'
        },
        'salt_low_state': {
            'resource': 'Low State',
            'icon_set': 'FontAwesome',
            'icon_char': 'f233',
        },
        'salt_minion': {
            'resource': 'Minion',
            'icon_set': 'FontAwesome',
            'icon_char': 'f233',
        },
        'salt_service': {
            'resource': 'Service',
            'icon_set': 'FontAwesome',
            'icon_char': 'f233',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'salt'
        super(SaltStackInput, self).__init__(**kwargs)

        try:
            self.name = kwargs['name']
        except KeyError:
            raise ValueError('Missing parameter name')

        config_data = load_yaml_json_file(kwargs['config_file'])
        self.config = config_data['configs'][self.name]
        self.api = Pepper(self.config['url'])
        self.api.login(self.config['auth']['username'],
                       self.config['auth']['password'],
                       'pam')

    def scrape_all_resources(self):
        self.scrape_minions()
        self.scrape_services()
        self.scrape_high_states()
        # self.scrape_low_states()

    def _create_relations(self):
        """
        for resource_id, resource in self.resources['salt_low_state'].items():
            # Define relationships between low states and nodes.
            self._scrape_relation(
                'salt_minion-salt_low_state',
                resource['metadata']['minion'],
                resource_id)
            split_service = resource['metadata']['__sls__'].split('.')
            self._scrape_relation(
                'salt_service-salt_low_state',
                '{}|{}.{}'.format(resource['metadata']['minion'],
                                  split_service[0], split_service[1]),
                resource_id)
        """
        for resource_id, resource in self.resources['salt_high_state'].items():
            # Define relationships between high states and nodes.
            self._scrape_relation(
                'salt_minion-salt_high_state',
                resource['metadata']['minion'],
                resource_id)
            split_service = resource['metadata']['__sls__'].split('.')
            self._scrape_relation(
                'salt_service-salt_high_state',
                '{}|{}.{}'.format(resource['metadata']['minion'],
                                  split_service[0], split_service[1]),
                resource_id)

        for resource_id, resource in self.resources['salt_service'].items():
            self._scrape_relation(
                'salt_service-salt_minion',
                resource_id,
                resource['metadata']['host'])

    def scrape_minions(self):
        response = self.api.low([{
            'client': 'local',
            'tgt': '*',
            'fun': 'grains.items'
        }]).get('return')[0]
        for minion_id, minion in response.items():
            self._scrape_resource(minion_id,
                                  minion_id,
                                  'salt_minion', None, metadata=minion)

    def scrape_services(self):
        response = self.api.low([{
            'client': 'local',
            'expr_form': 'compound',
            'tgt': 'I@salt:master',
            'fun': 'saltresource.graph_data'
        }]).get('return')[0]
        for minion_id, minion in response.items():
            for service in minion['graph']:
                self._scrape_resource('{}|{}'.format(minion_id,
                                                     service['service']),
                                      service['service'],
                                      'salt_service', None,
                                      metadata=service)

    def scrape_low_states(self):
        response = self.api.low([{
            'client': 'local',
            'tgt': '*',
            'fun': 'state.show_lowstate'
        }]).get('return')[0]
        for minion_id, low_states in response.items():
            for low_state in low_states:
                low_state['minion'] = minion_id
                self._scrape_resource('{}|{}|{}'.format(minion_id,
                                                        low_state['state'],
                                                        low_state['__id__']),
                                      '{} {}'.format(low_state['state'],
                                                     low_state['__id__']),
                                      'salt_low_state', None,
                                      metadata=low_state)

    def scrape_high_states(self):
        response = self.api.low([{
            'client': 'local',
            'tgt': '*',
            'fun': 'state.show_highstate'
        }]).get('return')[0]
        for minion_id, high_states in response.items():
            for high_state_id, high_state in high_states.items():
                high_state['minion'] = minion_id
                self._scrape_resource('{}|{}'.format(minion_id,
                                                     high_state_id),
                                      high_state_id,
                                      'salt_high_state', None,
                                      metadata=high_state)
