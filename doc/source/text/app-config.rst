
=============
Configuration
=============

You provide one configuration file for all providers. The default location is
``/etc/infra-scraper/config.yaml`` but it can be overriden by
``INFRA_SCRAPER_CONFIG_PATH`` environmental variable, for example:

.. code-block:: bash

    export INFRA_SCRAPER_CONFIG_PATH=~/scraper.yml


Configuration in ETCD
=====================

You can use ETCD as a storage backend for the configuration and scrape results. Following environmental parameters need to be set:

.. code-block:: bash

    export INFRA_SCRAPER_CONFIG_BACKEND=etcd
    export INFRA_SCRAPER_CONFIG_PATH=/service/scraper/config


Storage Configuration
=====================

You can set you local filesystem path where scraped data will be saved.

.. code-block:: yaml

    storage:
      backend: localfs
      path: /tmp/scraper
    endpoints: {}

You can also set the scraping storage backend to use the ETCD service instead
of a local filesystem backend.

.. code-block:: yaml

    storage:
      backend: etcd
      path: /scraper
    endpoints: {}


Endpoints Configuration
=======================

Each endpoint kind expects a little different set of configuration. Look at
individual chapters for samples of required parameters to setup individual
endpoints.
