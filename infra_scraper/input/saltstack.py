# -*- coding: utf-8 -*-

from pepper.libpepper import Pepper
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import load_yaml_json_file, setup_logger

logger = setup_logger('input.salt')


class SaltStackInput(BaseInput):

    RESOURCE_MAP = {
        'salt_high_state': {
            'resource': 'high_state',
            'client': '',
            'name': 'High State',
            'icon': 'fa:cube',
        },
        'salt_job': {
            'resource': 'job',
            'client': '',
            'name': 'Job',
            'icon': 'fa:clock-o',
        },
        'salt_low_state': {
            'resource': 'low_state',
            'client': '',
            'name': 'Low State',
            'icon': 'fa:cube',
        },
        'salt_minion': {
            'resource': 'minion',
            'client': '',
            'name': 'Minion',
            'icon': 'fa:server',
        },
        'salt_service': {
            'resource': 'service',
            'client': '',
            'name': 'Service',
            'icon': 'fa:podcast',
        },
        'salt_state_module': {
            'resource': 'state_module',
            'client': '',
            'name': 'State Module',
            'icon': 'fa:cubes',
        },
        'salt_user': {
            'resource': 'user',
            'client': '',
            'name': 'User',
            'icon': 'fa:user',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'salt'
        super(SaltStackInput, self).__init__(**kwargs)
        self.api = Pepper(self.config['auth_url'])
        self.api.login(self.config['username'],
                       self.config['password'],
                       'pam')

    def scrape_all_resources(self):
        self.scrape_jobs()
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
        for resource_id, resource in self.resources.get('salt_high_state', {}).items():
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

        for resource_id, resource in self.resources.get('salt_service', {}).items():
            self._scrape_relation(
                'salt_service-salt_minion',
                resource_id,
                resource['metadata']['host'])

        for resource_id, resource in self.resources.get('salt_job', {}).items():
            self._scrape_relation(
                'salt_user-salt_job',
                resource['metadata']['User'],
                resource_id)
            for minion_id, result in resource['metadata'].get('Result', {}).items():
                self._scrape_relation(
                    'salt_job-salt_minion',
                    resource_id,
                    minion_id)
                if type(result) is list:
                    logger.error(result[0])
                else:
                    for state_id, state in result.items():
                        if '__id__' in state:
                            result_id = '{}|{}'.format(minion_id, state['__id__'])
                            self._scrape_relation(
                                'salt_job-salt_high_state',
                                resource_id,
                                result_id)

    def scrape_jobs(self):
        response = self.api.low([{
            'client': 'runner',
            'fun': 'jobs.list_jobs',
            'arg': "search_function='[\"state.apply\", \"state.sls\"]'"
        }]).get('return')[0]
        for job_id, job in response.items():
            if job['Function'] in ['state.apply', 'state.sls']:
                result = self.api.lookup_jid(job_id).get('return')[0]
                job['Result'] = result
                self._scrape_resource(job_id,
                                      job['Function'],
                                      'salt_job', None, metadata=job)
                self._scrape_resource(job['User'],
                                      job['User'],
                                      'salt_user', None, metadata={})

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
            if type(high_states) is list:
                logger.error(high_states[0])
            else:
                for high_state_id, high_state in high_states.items():
                    high_state['minion'] = minion_id
                    self._scrape_resource('{}|{}'.format(minion_id,
                                                         high_state_id),
                                          high_state_id,
                                          'salt_high_state', None,
                                          metadata=high_state)
