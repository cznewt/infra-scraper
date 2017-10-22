
import os
import pykube
import logging
from requests.exceptions import HTTPError
from .base import BaseInput

logger = logging.getLogger(__name__)


class KubernetesInput(BaseInput):

    def __init__(self, **kwargs):
        self.kind = 'kubernetes'
        super(KubernetesInput, self).__init__(**kwargs)
        try:
            self.name = kwargs['name']
        except KeyError:
            raise ValueError('Missing parameter name.')

        self.config_file = kwargs.get('config_file', '{}/clusters.yaml'.format(
            os.path.dirname(os.path.realpath(__file__))))

        self.api = pykube.HTTPClient(pykube.KubeConfig.from_file(
                                     self.config_file))

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

    def _create_relations(self):

        namespace_2_uid = {}
        for resource_id, resource in self.resources['k8s:namespace'].items():
            resource_mapping = resource['metadata']['metadata']['name']
            namespace_2_uid[resource_mapping] = resource_id

        node_2_uid = {}
        for resource_id, resource in self.resources['k8s:node'].items():
            resource_mapping = resource['metadata']['metadata']['name']
            node_2_uid[resource_mapping] = resource_id

        service_run_2_uid = {}
        service_app_2_uid = {}
        for resource_id, resource in self.resources['k8s:service'].items():
            if resource['metadata']['spec'].get('selector', {}) is not None:
                if resource['metadata']['spec'].get('selector', {}).get('run', False):
                    selector = resource['metadata']['spec']['selector']['run']
                    service_run_2_uid[selector] = resource_id
                if resource['metadata']['spec'].get('selector', {}).get('app', False):
                    selector = resource['metadata']['spec']['selector']['app']
                    service_app_2_uid[selector] = resource_id

        # Add Containers as top-level resource
        """
        for resource_id, resource in self.resources['k8s:pod'].items():
            for container in resource['metadata']['spec']['containers']:
                container_id = "{1}-{2}".format(
                    resource['metadata']['uid'], container['name'])
                resources[container_id] = {
                    'metadata': container,
                    'kind': 'Container'
                }
                relations.append({
                    'source': resource_id,
                    'target': container_id,
                })
        """

        # Define relationships between namespace and all namespaced resources.
        for resource_type, resource_dict in self.resources.items():
            for resource_id, resource in resource_dict.items():
                if 'namespace' in resource['metadata']['metadata']:
                    self._scrape_relation(
                        '{}-k8s:namespace'.format(resource_type),
                        resource_id,
                        namespace_2_uid[resource['metadata']['metadata']['namespace']])

        # Define relationships between replica sets and deployments
        for resource_id, resource in self.resources['k8s:replica_set'].items():
            deployment_id = resource['metadata']['metadata']['ownerReferences'][0]['uid']
            self._scrape_relation(
                'k8s:deployment-k8s:replica_set',
                deployment_id,
                resource_id)

        for resource_id, resource in self.resources['k8s:pod'].items():
            # Define relationships between pods and nodes
            if resource['metadata']['spec']['nodeName'] is not None:
                node = resource['metadata']['spec']['nodeName']
                self._scrape_relation(
                    'k8s:pod-k8s:node',
                    resource_id,
                    node_2_uid[node])

            # Define relationships between pods and replication sets and
            # replication controllers.
            if resource['metadata']['metadata'].get('ownerReferences', False):
                if resource['metadata']['metadata']['ownerReferences'][0]['kind'] == 'ReplicaSet':
                    rep_set_id = resource['metadata']['metadata']['ownerReferences'][0]['uid']
                    self._scrape_relation(
                        'k8s:replica_set-k8s:pod',
                        rep_set_id,
                        resource_id)

            # Define relationships between pods and services.
            if resource['metadata']['metadata']['labels'].get('run', False):
                selector = resource['metadata']['metadata']['labels']['run']
                self._scrape_relation(
                    'k8s:pod-k8s:service',
                    resource_id,
                    service_run_2_uid[selector])
            if resource['metadata']['metadata']['labels'].get('app', False):
                try:
                    selector = resource['metadata']['metadata']['labels']['app']
                    self._scrape_relation(
                        'k8s:pod-k8s:service',
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

    def scrape_config_maps(self):
        response = pykube.ConfigMap.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:config_map')

    def scrape_cron_jobs(self):
        response = pykube.CronJob.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:blow_job')

    def scrape_daemon_sets(self):
        response = pykube.DaemonSet.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:daemon_set')

    def scrape_deployments(self):
        response = pykube.Deployment.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:deployment')

    def scrape_endpoints(self):
        response = pykube.Endpoint.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:endpoint')

    def scrape_events(self):
        response = pykube.Event.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:event')

    def scrape_horizontal_pod_autoscalers(self):
        response = pykube.HorizontalPodAutoscaler.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:horizontal_pod_autoscaler')

    def scrape_ingresses(self):
        response = pykube.Ingress.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:ingress')

    def scrape_jobs(self):
        response = pykube.Job.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:job')

    def scrape_namespaces(self):
        response = pykube.Namespace.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:namespace')

    def scrape_nodes(self):
        response = pykube.Node.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:node')

    def scrape_persistent_volumes(self):
        response = pykube.PersistentVolume.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:persistent_volume')

    def scrape_persistent_volume_claims(self):
        response = pykube.PersistentVolumeClaim.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:persistent_volume_claim')

    def scrape_pods(self):
        response = pykube.Pod.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:pod')

    def scrape_replica_sets(self):
        response = pykube.ReplicaSet.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:replica_set')

    def scrape_replication_controllers(self):
        response = pykube.ReplicationController.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:replication_controller')

    def scrape_roles(self):
        response = pykube.Role.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:role')

    def scrape_secrets(self):
        response = pykube.Secret.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:secret')

    def scrape_service_accounts(self):
        response = pykube.ServiceAccount.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:service_account')

    def scrape_services(self):
        response = pykube.Service.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:service')

    def scrape_stateful_sets(self):
        response = pykube.StatefulSet.objects(self.api)
        self._scrape_k8s_resources(response, 'k8s:stateful_set')
