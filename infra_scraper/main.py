
import importlib

from infra_scraper import constructors
from infra_scraper import exceptions


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
        module_class = _get_module("{}_{}".format(
            module_file, module_key))
        return module_class(**module_init)

    def scrape_data(self, name, kind, config):
        self.input = self._get_module('input', kind, config)
        self.input.scrape_all_resources()
        self.storage.save_data(name, self.input.to_dict())

    def get_data(self, name, kind, format='yaml'):
        data = self.storage.load_data(name)
        self.output = self._get_module('output', kind)
        return self.output.get_data(format, data)
