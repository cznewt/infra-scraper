
import logging
from .base import BaseInput
from infra_scraper.utils import load_yaml_json_file
from pepper.libpepper import Pepper
logger = logging.getLogger(__name__)


class SaltStackInput(BaseInput):

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
        self.scrape_low_states()

    def _create_relations(self):
        # Define relationships between low states and nodes.
        for resource_id, resource in self.resources['salt:low_state'].items():
            self._scrape_relation(
                'salt:minion-salt:low_state',
                resource['metadata']['minion'],
                resource_id)

    def scrape_minions(self):
        response = self.api.low([{
            'client': 'local',
            'tgt': '*',
            'fun': 'grains.items'
        }]).get('return')[0]
        for minion_id, minion in response.items():
            self._scrape_resource(minion_id,
                                  minion_id,
                                  'salt:minion', None, metadata=minion)

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
                                      'salt:low_state', None, metadata=low_state)
