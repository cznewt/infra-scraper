
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
