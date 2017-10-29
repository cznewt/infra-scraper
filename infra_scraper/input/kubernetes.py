# -*- coding: utf-8 -*-

import os
import yaml
import tempfile
import pykube
from requests.exceptions import HTTPError
from infra_scraper.input.base import BaseInput
from infra_scraper.utils import setup_logger

logger = setup_logger('input.kubernetes')


class KubernetesInput(BaseInput):

    RESOURCE_MAP = {
        'k8s_config_map': {
            'resource': 'ConfigMap',
            'name': 'Config Map',
            'icon': 'fa:file-text-o',
        },
        'k8s_container': {
            'resource': 'Container',
            'name': 'Container',
            'icon': 'fa:cube',
        },
        'k8s_cron_job': {
            'resource': 'CronJob',
            'name': 'Cron Job',
            'icon': 'fa:cube',
        },
        'k8s_deployment': {
            'resource': 'Deployment',
            'name': 'Deployment',
            'icon': 'fa:cubes',
        },
        'k8s_endpoint': {
            'resource': 'Endpoint',
            'name': 'Endpoint',
            'icon': 'fa:cube',
        },
        'k8s_event': {
            'resource': 'Event',
            'name': 'Event',
            'icon': 'fa:cube',
        },
        'k8s_job': {
            'resource': 'Job',
            'name': 'Job',
            'icon': 'fa:cube',
        },
        'k8s_namespace': {
            'resource': 'Namespace',
            'name': 'Namespace',
            'icon': 'fa:cube',
        },
        'k8s_node': {
            'resource': 'Node',
            'name': 'Node',
            'icon': 'fa:server',
        },
        'k8s_persistent_volume': {
            'resource': 'PersistentVolume',
            'name': 'Persistent Volume',
            'icon': 'fa:hdd-o',
        },
        'k8s_persistent_volume_claim': {
            'resource': 'PersistentVolumeClaim',
            'name': 'Persistent Volume Claim',
            'icon': 'fa:hdd-o',
        },
        'k8s_pod': {
            'resource': 'Pod',
            'name': 'Pod',
            'icon': 'fa:cubes',
        },
        'k8s_replica_set': {
            'resource': 'ReplicaSet',
            'name': 'Replica Set',
            'icon': 'fa:cubes',
        },
        'k8s_replication_controller': {
            'resource': 'ReplicationController',
            'name': 'Replication Controller',
            'icon': 'fa:cubes',
        },
        'k8s_role': {
            'resource': 'Role',
            'name': 'Role',
            'icon': 'fa:cube',
        },
        'k8s_secret': {
            'resource': 'Secret',
            'name': 'Secret',
            'icon': 'fa:lock',
        },
        'k8s_service': {
            'resource': 'Service',
            'name': 'Service',
            'icon': 'fa:podcast',
        },
        'k8s_service_account': {
            'resource': 'ServiceAccount',
            'name': 'Service Account',
            'icon': 'fa:user',
        },
    }

    def __init__(self, **kwargs):
        self.kind = 'kubernetes'
        self.scope = kwargs.get('scope', 'local')
        super(KubernetesInput, self).__init__(**kwargs)
        config_file, filename = tempfile.mkstemp()
        config_content = {
            'apiVersion': 'v1',
            'clusters': [{
                'cluster': self.config['cluster'],
                'name': self.name,
            }],
            'contexts': [{
                'context': {
                    'cluster': self.name,
                    'user': self.name,
                },
                'name': self.name,
            }],
            'current-context': self.name,
            'kind': 'Config',
            'preferences': {},
            'users': [{
                'name': self.name,
                'user': self.config['user']
            }]
        }
        os.write(config_file, yaml.safe_dump(config_content))
        os.close(config_file)
        self.config_wrapper = pykube.KubeConfig.from_file(filename)
        os.remove(filename)
        self.api = pykube.HTTPClient(self.config_wrapper)

    def scrape_all_resources(self):
        self.scrape_config_maps()
        self.scrape_cron_jobs()
        self.scrape_daemon_sets()
        self.scrape_deployments()
        self.scrape_endpoints()
        self.scrape_events()
        self.scrape_horizontal_pod_autoscalers()
        self.scrape_ingresses()
        self.scrape_jobs()
        self.scrape_namespaces()
        self.scrape_nodes()
        self.scrape_persistent_volumes()
        self.scrape_persistent_volume_claims()
        self.scrape_pods()
        self.scrape_replica_sets()
        self.scrape_replication_controllers()
        self.scrape_roles()
        self.scrape_secrets()
        self.scrape_service_accounts()
        self.scrape_services()
        self.scrape_stateful_sets()
        self.scrape_containers()

    def _create_relations(self):

        namespace_2_uid = {}
        for resource_id, resource in self.resources.get('k8s_namespace', {}).items():
            resource_mapping = resource['metadata']['metadata']['name']
            namespace_2_uid[resource_mapping] = resource_id

        node_2_uid = {}
        for resource_id, resource in self.resources.get('k8s_node', {}).items():
            resource_mapping = resource['metadata']['metadata']['name']
            node_2_uid[resource_mapping] = resource_id

        secret_2_uid = {}
        for resource_id, resource in self.resources.get('k8s_secret', {}).items():
            resource_mapping = resource['metadata']['metadata']['name']
            secret_2_uid[resource_mapping] = resource_id

        volume_2_uid = {}
        for resource_id, resource in self.resources.get('k8s_persistent_volume', {}).items():
            resource_mapping = resource['metadata']['metadata']['name']
            volume_2_uid[resource_mapping] = resource_id

        service_run_2_uid = {}
        service_app_2_uid = {}
        for resource_id, resource in self.resources.get('k8s_service', {}).items():
            if resource['metadata']['spec'].get('selector', {}) is not None:
                if resource['metadata']['spec'].get('selector', {}).get('run', False):
                    selector = resource['metadata']['spec']['selector']['run']
                    service_run_2_uid[selector] = resource_id
                if resource['metadata']['spec'].get('selector', {}).get('app', False):
                    selector = resource['metadata']['spec']['selector']['app']
                    service_app_2_uid[selector] = resource_id

        # Define relationships between namespace and all namespaced resources.
        for resource_type, resource_dict in self.resources.items():
            for resource_id, resource in resource_dict.items():
                if 'namespace' in resource.get('metadata', {}).get('metadata', {}):
                    self._scrape_relation(
                        '{}-k8s_namespace'.format(resource_type),
                        resource_id,
                        namespace_2_uid[resource['metadata']['metadata']['namespace']])

        # Define relationships between service accounts and secrets
        for resource_id, resource in self.resources.get('k8s_service_account', {}).items():
            for secret in resource['metadata']['secrets']:
                self._scrape_relation('k8s_service_account-k8s_secret',
                                      resource_id,
                                      secret_2_uid[secret['name']])
        """
        for resource_id, resource in self.resources['k8s_persistent_volume'].items():
            self._scrape_relation('k8s_persistent_volume-k8s_persistent_volume_claim',
                                  resource_id,
                                  volume_2_uid[resource['spec']['volumeName']])
        """

        # Define relationships between replica sets and deployments
        for resource_id, resource in self.resources.get('k8s_replica_set', {}).items():
            deployment_id = resource['metadata']['metadata']['ownerReferences'][0]['uid']
            self._scrape_relation(
                'k8s_deployment-k8s_replica_set',
                deployment_id,
                resource_id)

        for resource_id, resource in self.resources.get('k8s_pod', {}).items():
            # Define relationships between pods and nodes
            if resource['metadata']['spec']['nodeName'] is not None:
                node = resource['metadata']['spec']['nodeName']
                self._scrape_relation('k8s_pod-k8s_node',
                                      resource_id,
                                      node_2_uid[node])

            # Define relationships between pods and replication sets and
            # replication controllers.
            if resource['metadata']['metadata'].get('ownerReferences', False):
                if resource['metadata']['metadata']['ownerReferences'][0]['kind'] == 'ReplicaSet':
                    rep_set_id = resource['metadata']['metadata']['ownerReferences'][0]['uid']
                    self._scrape_relation(
                        'k8s_replica_set-k8s_pod',
                        rep_set_id,
                        resource_id)

            # Define relationships between pods and services.
            if resource['metadata']['metadata']['labels'].get('run', False):
                selector = resource['metadata']['metadata']['labels']['run']
                self._scrape_relation(
                    'k8s_pod-k8s_service',
                    resource_id,
                    service_run_2_uid[selector])
            if resource['metadata']['metadata']['labels'].get('app', False):
                try:
                    selector = resource['metadata']['metadata']['labels']['app']
                    self._scrape_relation(
                        'k8s_pod-k8s_service',
                        resource_id,
                        service_app_2_uid[selector])
                except Exception:
                    pass

    def _scrape_k8s_resources(self, response, kind):
        try:
            for item in response:
                resource = item.obj
                self._scrape_resource(resource['metadata']['uid'],
                                      resource['metadata']['name'],
                                      kind, None, metadata=resource)
        except HTTPError as e:
            logger.error(e)

    def scrape_containers(self):
        for resource_id, resource in self.resources['k8s_pod'].items():
            for container in resource['metadata']['spec']['containers']:
                container_id = "{}-{}".format(resource_id,
                                              container['name'])
                self._scrape_resource(container_id,
                                      container['name'],
                                      'k8s_container', None,
                                      metadata=container)
                self._scrape_relation('k8s_pod-k8s_container',
                                      resource_id,
                                      container_id)

    def scrape_config_maps(self):
        response = pykube.ConfigMap.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_config_map')

    def scrape_cron_jobs(self):
        response = pykube.CronJob.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_blow_job')

    def scrape_daemon_sets(self):
        response = pykube.DaemonSet.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_daemon_set')

    def scrape_deployments(self):
        response = pykube.Deployment.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_deployment')

    def scrape_endpoints(self):
        response = pykube.Endpoint.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_endpoint')

    def scrape_events(self):
        response = pykube.Event.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_event')

    def scrape_horizontal_pod_autoscalers(self):
        response = pykube.HorizontalPodAutoscaler.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_horizontal_pod_autoscaler')

    def scrape_ingresses(self):
        response = pykube.Ingress.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_ingress')

    def scrape_jobs(self):
        response = pykube.Job.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_job')

    def scrape_namespaces(self):
        response = pykube.Namespace.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_namespace')

    def scrape_nodes(self):
        response = pykube.Node.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_node')

    def scrape_persistent_volumes(self):
        response = pykube.PersistentVolume.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_persistent_volume')

    def scrape_persistent_volume_claims(self):
        response = pykube.PersistentVolumeClaim.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_persistent_volume_claim')

    def scrape_pods(self):
        response = pykube.Pod.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_pod')

    def scrape_replica_sets(self):
        response = pykube.ReplicaSet.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_replica_set')

    def scrape_replication_controllers(self):
        response = pykube.ReplicationController.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_replication_controller')

    def scrape_roles(self):
        response = pykube.Role.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_role')

    def scrape_secrets(self):
        response = pykube.Secret.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_secret')

    def scrape_service_accounts(self):
        response = pykube.ServiceAccount.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_service_account')

    def scrape_services(self):
        response = pykube.Service.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_service')

    def scrape_stateful_sets(self):
        response = pykube.StatefulSet.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s_stateful_set')
