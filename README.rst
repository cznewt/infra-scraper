
==============================
Infrastucture Metadata Scraper
==============================

Get your live infrastructure topology data from your favorite resource
providers for further processing, visualialitions, etc. Currently supported
providers are:

* Kubernetes
* OpenStack
* SaltStack

Installation
============

To bootstrap development environment run following commands:

.. code-block:: bash

    git clone git@github.com:cznewt/infra-scraper.git
    cd infra-scraper
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt


Configuration
=============

You provide separate configuration files for differt provider kinds.


Kubernetes
----------

Kubernetes requires kubeconfig file. You provide name of the context to the
scraper.

.. code-block:: yaml

    ---
    apiVersion: v1
    clusters:
    - cluster:
        certificate-authority-data: |
          cacert
        server: https://kubernetes.api:443
      name: kubernetes-cluster
    contexts:
    - context:
        cluster: kubernetes-cluster
        user: kubernetes-cluster-admin
      name: kubernetes-cluster
    current-context: kubernetes-cluster
    kind: Config
    preferences: {}
    users:
    - name: kubernetes-cluster-admin
      user:
        client-certificate-data: |
          clientcert
        client-key-data: |
          clientkey

OpenStack
---------

Example configuration for keystone v2 and keystone v3 clouds in
`os_client_config` format.

.. code-block:: yaml

    clouds:
      keystone2:
        region_name: RegionOne
        auth:
          username: 'admin'
          password: 'password'
          project_name: 'admin'
          auth_url: 'https://keystone.api:5000/v2.0'
      keystone3:
        region_name: RegionOne
        identity_api_version: '3'
        auth:
          username: 'admin'
          password: 'password'
          project_name: 'admin'
          domain_name: 'default'
          auth_url: 'https://keystone.api:5000/v3'

SaltStack
---------

Configuration for connecting to Salt API.

.. code-block:: yaml

    configs:
      salt:
        url: 'https://salt-api:8000'
        verify: False
        auth:
          username: 'user'
          password: 'password'


Supported Metadata
==================

Following outputs show available resources and relations from given domain.


Kubernetes
----------

.. code-block:: yaml

    kind: kubernetes
    name: test-kubernetes
    relations:
      k8s:deployment-k8s:namespace: 22
      k8s:deployment-k8s:replica_set: 62
      k8s:endpoint-k8s:namespace: 28
      k8s:event-k8s:namespace: 52
      k8s:persistent_volume_claim-k8s:namespace: 1
      k8s:pod-k8s:namespace: 52
      k8s:pod-k8s:node: 52
      k8s:pod-k8s:service: 52
      k8s:replica_set-k8s:namespace: 62
      k8s:replica_set-k8s:pod: 51
      k8s:replication_controller-k8s:namespace: 1
      k8s:secret-k8s:namespace: 1
      k8s:service-k8s:namespace: 30
      k8s:service_account-k8s:namespace: 1
    resources:
      k8s:deployment: 22
      k8s:endpoint: 28
      k8s:event: 52
      k8s:namespace: 4
      k8s:node: 5
      k8s:persistent_volume: 1
      k8s:persistent_volume_claim: 1
      k8s:pod: 52
      k8s:replica_set: 62
      k8s:replication_controller: 1
      k8s:secret: 1
      k8s:service: 30
      k8s:service_account: 1
    timestamp: 1508692477


OpenStack
---------

.. code-block:: yaml

    kind: openstack
    name: test-openstack
    relations:
      os:floating_ip-os:project: 617
      os:hypervisor-os:aggregate: 46
      os:network-os:project: 575
      os:port-os:hypervisor: 3183
      os:port-os:network: 3183
      os:port-os:project: 3183
      os:port-os:server: 3183
      os:router-os:project: 42
      os:server-os:flavor: 676
      os:server-os:hypervisor: 676
      os:server-os:project: 676
      os:stack-os:network: 7
      os:stack-os:port: 17
      os:stack-os:project: 2
      os:stack-os:server: 7
      os:stack-os:subnet: 7
      os:subnet-os:network: 567
      os:subnet-os:project: 567
    resources:
      os:aggregate: 13
      os:flavor: 43
      os:floating_ip: 617
      os:hypervisor: 72
      os:network: 575
      os:port: 3183
      os:resource_type: 169
      os:router: 42
      os:server: 676
      os:stack: 2
      os:subnet: 567
      os:volume: 10
    timestamp: 1508694475


SaltStack
---------

.. code-block:: yaml

    kind: salt
    name: test-salt
    relations:
      salt_job-salt_high_state: 552
      salt_job-salt_minion: 9
      salt_minion-salt_high_state: 689
      salt_service-salt_high_state: 689
      salt_service-salt_minion: 24
      salt_user-salt_job: 7
    resources:
      salt_high_state: 689
      salt_job: 7
      salt_minion: 3
      salt_service: 24
      salt_user: 2
    timestamp: 1508932328
