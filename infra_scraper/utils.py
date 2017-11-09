
import os
import re
import json
import yaml
import logging

_schema_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'schema')


def setup_logger(name):
    msg_format = '%(asctime)s [%(levelname)s] [%(module)s] %(message)s'
    formatter = logging.Formatter(fmt=msg_format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def load_yaml_json_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            if path.endswith('json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)
    return {}


def get_graph_schema(name):
    schema_file = os.path.join(_schema_dir, 'resource', '{}.yaml'.format(name))
    return load_yaml_json_file(schema_file)


def get_node_icon(icon):
    family, character = icon.split(":")
    output = ICON_MAPPING['character'][family][character].copy()
    output["family"] = ICON_MAPPING['family'][family]
    output['name'] = character
    output["char"] = int("0x{}".format(output["char"]), 0)
    return output


def to_camel_case(snake_str, first=True):
    components = snake_str.split('_')
    if first:
        return "".join(x.title() for x in components)
    else:
        return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class ClassRegistry:

    def __init__(self):
        self._classes = {}

    def add(self, cls):
        self._classes[cls.__name__] = cls

    def get_type(self, name):
        return self._classes.get(name)


icon_file = os.path.join(_schema_dir, 'icon.yaml')
ICON_MAPPING = load_yaml_json_file(icon_file)
