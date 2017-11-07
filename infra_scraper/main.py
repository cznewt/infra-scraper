
import os
import importlib
import time

from infra_scraper import constructors
from infra_scraper import exceptions
from infra_scraper.utils import load_yaml_json_file, setup_logger

logger = setup_logger(__name__)

config_backend = os.environ.get('INFRA_SCRAPER_CONFIG_BACKEND',
                                'localfs')
config_file = os.environ.get('INFRA_SCRAPER_CONFIG_PATH',
                             '/etc/infra-scraper/config.yaml')


def _get_module(module_key):
    class_mapping = constructors.get_constructor_mapping()
    if module_key not in class_mapping:
        raise exceptions.InfraScraperException(
            "Service {module_key} is unkown. Please pass in a client"
            " constructor or submit a patch to infra scraper".format(
                module_key=module_key))
    mod_name, ctr_name = class_mapping[module_key].rsplit('.', 1)
    lib_name = mod_name.split('.')[0]
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        raise exceptions.InfraScraperException(
            "Client for '{module_key}' was requested, but"
            " {mod_name} was unable to be imported. Either import"
            " the module yourself and pass the constructor in as an argument,"
            " or perhaps you do not have module {lib_name} installed.".format(
                module_key=module_key,
                mod_name=mod_name,
                lib_name=lib_name))
    try:
        ctr = getattr(mod, ctr_name)
    except AttributeError:
        raise exceptions.InfraScraperException(
            "Client for '{module_key}' was requested, but although"
            " {mod_name} imported fine, the constructor at {fullname}"
            " as not found.".format(
                module_key=module_key,
                mod_name=mod_name,
                fullname=class_mapping[module_key]))
    return ctr


class InfraScraper(object):
    def __init__(self):
        self.storage = self._get_module('storage', 'file')

    def _get_module(self, module_file, module_key, module_init={}):
        module_class = _get_module("{}-{}".format(
            module_file, module_key))
        return module_class(**module_init)

    def get_global_config(self):
        return load_yaml_json_file(config_file)

    def get_config(self, name):
        config = self.get_global_config()['endpoints'][name]
        config['name'] = name
        return config

    def status(self):
        config = self.get_global_config()
        for endpoint_name, endpoint in config['endpoints'].items():
            endpoint.pop('config')
            endpoint['status'] = self.get_endpoint_status(endpoint_name)
        return config

    def get_endpoint_status(self, name):
        try:
            data = self.get_cached_data(name, 'count')
        except Exception as e:
            logger.error('Cannot get last status for {}, with error {}.'.format(name, e))
            data = None
        return data

    def scrape_all_data_forever(self, interval):
        config = self.get_global_config()
        while True:
            for endpoint_name, endpoint in config['endpoints'].items():
                self.scrape_data(endpoint_name)
            time.sleep(config.get('scrape_interval', 60))

    def scrape_all_data(self):
        config = self.get_global_config()
        for endpoint_name, endpoint in config['endpoints'].items():
            try:
                self.scrape_data(endpoint_name)
            except Exception as e:
                logger.error('Scraping endpoing {} failed with error: {}'.format(endpoint_name, e))

    def scrape_data_forever(self, name, interval):
        config = self.get_global_config()
        sleep_interval = config.get('scrape_interval', interval)
        while True:
            self.scrape_data(name)
            logger.info('Sleeping for {} seconds.'.format(sleep_interval))
            time.sleep(sleep_interval)

    def scrape_data(self, name):
        config = self.get_config(name)
        self.input = self._get_module('input', config['kind'], config)
        self.out_count = self._get_module('output', 'count')
        self.out_vis = self._get_module('output', 'vis')
        self.out_vis_hier = self._get_module('output', 'vis-hier')
        logger.info('Scraping of {} started.'.format(name))
        self.input.scrape_all_resources()
        data = self.input.to_dict()
        self.storage.save_data(name, data.copy())
        self.storage.save_output_data(name, 'count',
                                      self.out_count.get_data('raw', data.copy()))
        self.storage.save_output_data(name, 'vis',
                                      self.out_vis.get_data('raw', data.copy()))
        self.storage.save_output_data(name, 'vis-hier',
                                      self.out_vis_hier.get_data('raw', data.copy()))
        logger.info('Scraping of {} completed.'.format(name))

    def get_cached_data(self, name, kind):
        storage = self._get_module('storage', 'file')
        data = storage.load_output_data(name, kind)
        return data

    def get_data(self, name, kind, format='raw'):
        self.output = self._get_module('output', kind)
        data = self.storage.load_data(name)
        return self.output.get_data(format, data)
