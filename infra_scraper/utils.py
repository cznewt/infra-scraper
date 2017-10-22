
import os
import json
import yaml


def load_yaml_json_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            if path.endswith('json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)
    return {}
