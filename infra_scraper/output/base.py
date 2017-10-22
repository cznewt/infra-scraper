
import yaml
import logging

logger = logging.getLogger(__name__)


class BaseOutput(object):

    def __init__(self, **kwargs):
        pass

    def get_data(self, data_format='yaml', data={}):
        if data_format == 'yaml':
            return self.yaml_output(self.transform_data(data))

    def yaml_output(self, data):
        return yaml.safe_dump(data, default_flow_style=False)
