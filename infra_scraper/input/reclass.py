# -*- coding: utf-8 -*-

from infra_scraper.input.saltstack import SaltStackInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.reclass')


class SaltReclassInput(SaltStackInput):

    def __init__(self, **kwargs):
        super(SaltReclassInput, self).__init__(**kwargs)
        self.kind = 'salt'

    def _create_relations(self):
        for resource_id, resource in self.resources.get('salt_job', {}).items():
            for minion_id, result in resource['metadata'].get('Result', {}).items():
                self._scrape_relation(
                    'on_salt_minion',
                    resource_id,
                    minion_id)

    def scrape_all_resources(self):
        self.scrape_minions()
        self.scrape_resources()
        self.scrape_jobs()
#        self.scrape_services()

    def scrape_resources(self):
        response = self.api.low([{
            'client': 'local',
            'expr_form': 'compound',
            'tgt': 'I@salt:master',
            'fun': 'reclass.graph_data'
        }]).get('return')[0]
        for minion_id, minion in response.items():
            for service in minion['graph']:
                service_id = '{}|{}'.format(service['host'],
                                            service['service'])
                self._scrape_resource(service_id,
                                      service['service'],
                                      'salt_service', None,
                                      metadata=service)
                self._scrape_relation(
                    'on_salt_minion',
                    service_id,
                    service['host'])
                for rel in service['relations']:
                    if rel['host'] not in self.resources['salt_minion']:
                        self._scrape_resource(rel['host'],
                                              rel['host'],
                                              'salt_minion', None,
                                              metadata={})
                    rel_service_id = '{}|{}'.format(rel['host'],
                                                    rel['service'])
                    if rel_service_id not in self.resources['salt_service']:
                        self._scrape_resource(rel_service_id,
                                              rel['service'],
                                              'salt_service', None,
                                              metadata={})
                        self._scrape_relation(
                            'on_salt_minion',
                            rel_service_id,
                            rel['host'])
                    self._scrape_relation(
                        'requires_salt_service',
                        service_id,
                        rel_service_id)

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
