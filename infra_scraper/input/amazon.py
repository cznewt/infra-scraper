# -*- coding: utf-8 -*-

import yaml
import boto3
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.aws')


class AmazonWebServicesInput(BaseInput):

    RESOURCE_MAP = {
        's3_bucket': {
            'resource': 's3_bucket',
            'client': 's3',
            'name': 'S3 Bucket',
            'icon': 'fa:hdd-o',
        },
        'ec2_instance': {
            'resource': 'ec2_instance',
            'client': 'ec2',
            'name': 'EC2 Instance',
            'icon': 'fa:server',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'aws'
        self.scope = kwargs.get('scope', 'local')
        super(AmazonWebServicesInput, self).__init__(**kwargs)
        self.ec2_client = boto3.resource('ec2')
        self.s3_client = boto3.resource('s3')

    def scrape_all_resources(self):
        self.scrape_ec2_instances()
        self.scrape_s3_buckets()

    def _create_relations(self):
        pass

    def scrape_ec2_instances(self):
        for item in self.ec2_client.instances.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['InstanceId'],
                                  resource['data']['InstanceId'],
                                  'ec2_instance', None, metadata=resource)

    def scrape_s3_buckets(self):
        for item in self.s3_client.buckets.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['Name'],
                                  resource['data']['Name'],
                                  's3_bucket', None, metadata=resource)
