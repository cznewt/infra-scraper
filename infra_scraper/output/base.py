
import yaml
import json
import logging

logger = logging.getLogger(__name__)


class BaseOutput(object):

    def __init__(self, **kwargs):
        pass

    def get_data(self, data_format='raw', data={}):
        if data_format == 'yaml':
            return self.yaml_output(self.transform_data(data))
        elif data_format == 'json':
            return self.json_output(self.transform_data(data))
        else:
            return self.transform_data(data)

    def yaml_output(self, data):
        return yaml.safe_dump(data, default_flow_style=False)

    def json_output(self, data):
        return json.dumps(data)
