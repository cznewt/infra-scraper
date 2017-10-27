
import os
import json
import yaml
import logging


def load_yaml_json_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            if path.endswith('json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)
    return {}


def setup_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] [%(module)s] %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
