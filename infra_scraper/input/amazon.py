# -*- coding: utf-8 -*-

import boto3
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.aws')


class AmazonWebServicesInput(BaseInput):

    def __init__(self, **kwargs):
        self.kind = 'aws'
        self.scope = kwargs.get('scope', 'local')
        super(AmazonWebServicesInput, self).__init__(**kwargs)
        self.ec2_client = boto3.resource('ec2')
        self.s3_client = boto3.resource('s3')

    def scrape_all_resources(self):
#        self.scrape_ec2_images()
#        self.scrape_ec2_elastic_ips()
        self.scrape_ec2_instances()
        self.scrape_ec2_internet_gateways()
        self.scrape_ec2_subnets()
        self.scrape_ec2_vpcs()
        self.scrape_ec2_key_pairs()
        self.scrape_s3_buckets()

    def _create_relations(self):
        for resource_id, resource in self.resources.get('ec2_instance', {}).items():
            if 'VpcId' in resource['metadata']:
                if resource['metadata']['VpcId'] in self.resources.get('ec2_vpc', {}):
                    self._scrape_relation(
                        'in_ec2_vpc',
                        resource_id,
                        resource['metadata']['VpcId'])

            if 'KeyName' in resource['metadata']:
                if resource['metadata']['KeyName'] in self.resources.get('ec2_key_pair', {}):
                    self._scrape_relation(
                        'using_ec2_key_pair',
                        resource_id,
                        resource['metadata']['KeyName'])

            if 'SubnetId' in resource['metadata']:
                if resource['metadata']['SubnetId'] in self.resources.get('ec2_subnet', {}):
                    self._scrape_relation(
                        'in_ec2_subnet',
                        resource_id,
                        resource['metadata']['SubnetId'])

    def scrape_ec2_elastic_ips(self):
        for item in self.ec2_client.eips.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['InternetGatewayId'],
                                  resource['data']['InternetGatewayId'],
                                  'ec2_internet_gateway', None, metadata=resource['data'])

    def scrape_ec2_images(self):
        for item in self.ec2_client.images.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            if 'Name' in resource['data']:
                image_name = resource['data']['Name']
            else:
                image_name = resource['data']['ImageId']
            self._scrape_resource(resource['data']['ImageId'],
                                  image_name,
                                  'ec2_image', None, metadata=resource['data'])

    def scrape_ec2_instances(self):
        for item in self.ec2_client.instances.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            try:
                name = resource['data']['NetworkInterfaces'][0]['Association']['PublicDnsName']
            except Exception:
                name = resource['data']['InstanceId']
            print(resource['data'])
            self._scrape_resource(resource['data']['InstanceId'],
                                  name,
                                  'ec2_instance', None, metadata=resource['data'])

    def scrape_ec2_internet_gateways(self):
        for item in self.ec2_client.internet_gateways.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['InternetGatewayId'],
                                  resource['data']['InternetGatewayId'],
                                  'ec2_internet_gateway', None, metadata=resource['data'])

    def scrape_ec2_key_pairs(self):
        for item in self.ec2_client.key_pairs.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['KeyName'],
                                  resource['data']['KeyName'],
                                  'ec2_key_pair', None, metadata=resource['data'])

    def scrape_ec2_subnets(self):
        for item in self.ec2_client.subnets.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['SubnetId'],
                                  resource['data']['SubnetId'],
                                  'ec2_subnet', None, metadata=resource['data'])

    def scrape_ec2_vpcs(self):
        for item in self.ec2_client.vpcs.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            name = resource['data']['VpcId']
            for tag in resource['data'].get('Tags', {}):
                if tag['Key'] == 'Name':
                    name = tag['Value']
            self._scrape_resource(resource['data']['VpcId'],
                                  name,
                                  'ec2_vpc', None, metadata=resource['data'])

    def scrape_s3_buckets(self):
        for item in self.s3_client.buckets.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            self._scrape_resource(resource['data']['Name'],
                                  resource['data']['Name'],
                                  's3_bucket', None, metadata=resource['data'])
