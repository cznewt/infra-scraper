
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

Openstack
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


Documentation
=============

Full documenation is available at [infra-scraper.readthedocs.io](http://infra-scraper.readthedocs.io).
