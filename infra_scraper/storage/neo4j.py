
from .base import BaseStorage
import os
import glob
import yaml
import logging

from infra_scraper.utils import to_camel_case, ClassRegistry

from neomodel import config, StructuredNode, StringProperty, IntegerProperty, JSONProperty
from neomodel.match import OUTGOING, INCOMING, EITHER
from neomodel.relationship_manager import RelationshipManager
from neomodel.relationship import StructuredRel


logger = logging.getLogger(__name__)

registry = ClassRegistry()


class ResourceRel(StructuredRel):
    size = IntegerProperty(default=1)
    status = StringProperty(default='unknown')


class RelationshipDefinition(object):
    def __init__(self, relation_type, cls_name, direction, manager=RelationshipManager, model=None):
        self._raw_class = cls_name
        self.manager = manager
        self.definition = {}
        self.definition['relation_type'] = relation_type
        self.definition['direction'] = direction
        self.definition['model'] = model

    def _lookup_node_class(self):
        if not isinstance(self._raw_class, str):
            self.definition['node_class'] = self._raw_class
        else:
            name = self._raw_class
            self.definition['node_class'] = registry.get_type(name)

    def build_manager(self, source, name):
        self._lookup_node_class()
        return self.manager(source, name, self.definition)


class ZeroOrMore(RelationshipManager):
    """
    A relationship of zero or more nodes (the default)
    """
    description = "zero or more relationships"


def _relate(cls_name, direction, rel_type, cardinality=None, model=None):

    if model and not issubclass(model, (StructuredRel,)):
        raise ValueError('model must be a StructuredRel')
    return RelationshipDefinition(rel_type, cls_name, direction, cardinality, model)


def RelationshipTo(cls_name, rel_type, cardinality=ZeroOrMore, model=None):
    return _relate(cls_name, OUTGOING, rel_type, cardinality, model)


def RelationshipFrom(cls_name, rel_type, cardinality=ZeroOrMore, model=None):
    return _relate(cls_name, INCOMING, rel_type, cardinality, model)


def Relationship(cls_name, rel_type, cardinality=ZeroOrMore, model=None):
    return _relate(cls_name, EITHER, rel_type, cardinality, model)


class Neo4jStorage(BaseStorage):

    def __init__(self, **kwargs):
        super(Neo4jStorage, self).__init__(**kwargs)
        config.DATABASE_URL = kwargs['database_url']

    def convert_relations(self, relation_types):
        for relation_name, relation in relation_types.items():
            registry.add(type(
                relation_name,
                (ResourceRel,),
                relation.get('model', {})))

    def convert_resources(self, resource_types):
        for resource_name, resource in resource_types.items():
            fields = {
                'uid': StringProperty(unique_index=True),
                'name': StringProperty(required=True),
                'kind': StringProperty(required=True),
                'metadata': JSONProperty(required=True),
            }
            for field_name, field in resource.get('model', {}).items():
                cls_name = field.pop("type")
                target_cls = field.pop('target')
                model_name = field.pop('model')
                field['model'] = registry.get_type(model_name)
                fields[field_name] = globals().get(to_camel_case(cls_name))(target_cls, model_name, **field)
            registry.add(type(resource_name,
                         (StructuredNode,), fields))

    def _get_last_timestamp(self, name):
        sinks = glob.glob('{}/*.yaml'.format(self._get_storage_dir(name)))
        last_sink = max(sinks, key=os.path.getctime)
        return last_sink.split('/')[-1].replace('.yaml', '')

    def save_data(self, name, data):
        self.convert_relations(data['relation_types'])
        self.convert_resources(data['resource_types'])

        resources = {}

        for resource_type_name, resource_type in data['resources'].items():
            cls = registry.get_type(resource_type_name)
            for resource_name, resource in resource_type.items():
                # import pdb; pdb.set_trace()
                resources[resource['uid']] = cls(**resource).save()
        for relation_type_name, relation_type in data['relations'].items():
            for relation in relation_type:
                if relation['source'] in resources and relation['target'] in resources:
                    source = resources[relation['source']]
                    target = resources[relation['target']]
                    try:
                        rel_field = data['relation_types'][relation_type_name]['relation'][source.kind]
                    except:
                        rel_field = data['relation_types'][relation_type_name]['relation']['default']
                    relation = getattr(source, rel_field).build_manager(source, relation_type_name)
                    relation.connect(target, {})

        self.last_timestamp = data['timestamp']

    def load_data(self, name):
        data = None
        self.last_timestamp = self._get_last_timestamp(name)
        filename = '{}/{}.yaml'.format(self._get_storage_dir(name),
                                       self.last_timestamp)
        with open(filename, 'r') as stream:
            try:
                data = yaml.load(stream)
            except yaml.YAMLError as exception:
                logger.error(exception)
        stream.close()
        return data

    def save_output_data(self, name, kind, data):
        pass

    def load_output_data(self, name, kind):
        pass
