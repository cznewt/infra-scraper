# -*- coding: utf-8 -*-

import yaml
import boto3
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.aws')


class AmazonWebServicesInput(BaseInput):

    RESOURCE_MAP = {
        's3_bucket': {
            'resource': 'AWS::S3::Bucket',
            'client': 's3',
            'name': 'Bucket',
            'icon': 'fa:hdd-o',
        },
        'ec2_elastic_ip': {
            'resource': 'AWS::EC2::EIP',
            'client': 'ec2',
            'name': 'Elastic IP',
            'icon': 'fa:cube',
        },
        'ec2_elastic_ip_association': {
            'resource': 'AWS::EC2::EIPAssociation',
            'client': 'ec2',
            'name': 'Elastic IP Association',
            'icon': 'fa:cube',
        },
        'ec2_instance': {
            'resource': 'AWS::EC2::Instance',
            'client': 'ec2',
            'name': 'Instance',
            'icon': 'fa:server',
        },
        'ec2_internet_gateway': {
            'resource': 'AWS::EC2::InternetGateway',
            'client': 'ec2',
            'name': 'Internet Gateway',
            'icon': 'fa:cube',
        },
        'ec2_key_pair': {
            'resource': 'AWS::EC2::KeyPair',
            'client': 'ec2',
            'name': 'Key Pair',
            'icon': 'fa:key',
        },
        'ec2_subnet': {
            'resource': 'AWS::EC2::Subnet',
            'client': 'ec2',
            'name': 'Subnet',
            'icon': 'fa:cube',
        },
        'ec2_vpc': {
            'resource': 'AWS::EC2::VPC',
            'client': 'ec2',
            'name': 'VPC',
            'icon': 'fa:cubes',
        },
        'ec2_vpc_gateway_attachment': {
            'resource': 'AWS::EC2::VPCGatewayAttachment',
            'client': 'ec2',
            'name': 'VPC Gateway Attachment',
            'icon': 'fa:cube',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'aws'
        self.scope = kwargs.get('scope', 'local')
        super(AmazonWebServicesInput, self).__init__(**kwargs)
        self.ec2_client = boto3.resource('ec2')
        self.s3_client = boto3.resource('s3')

    def scrape_all_resources(self):
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
                        'ec2_instance-ec2_vpc',
                        resource_id,
                        resource['metadata']['VpcId'])

            if 'KeyName' in resource['metadata']:
                if resource['metadata']['KeyName'] in self.resources.get('ec2_key_pair', {}):
                    self._scrape_relation(
                        'ec2_instance-ec2_key_pair',
                        resource_id,
                        resource['metadata']['KeyName'])

            if 'SubnetId' in resource['metadata']:
                if resource['metadata']['SubnetId'] in self.resources.get('ec2_subnet', {}):
                    self._scrape_relation(
                        'ec2_instance-ec2_subnet',
                        resource_id,
                        resource['metadata']['SubnetId'])

    def scrape_ec2_elastic_ips(self):
        for item in self.ec2_client.eips.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            print resource
            self._scrape_resource(resource['data']['InternetGatewayId'],
                                  resource['data']['InternetGatewayId'],
                                  'ec2_internet_gateway', None, metadata=resource['data'])

    def scrape_ec2_instances(self):
        for item in self.ec2_client.instances.all():
            resource = item.meta.__dict__
            resource.pop('resource_model')
            resource.pop('client')
            try:
                name =  resource['data']['NetworkInterfaces'][0]['Association']['PublicDnsName']
            except Exception:
                name = resource['data']['InstanceId']
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
