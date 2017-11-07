
import pytest
import json
import os

from infra_scraper.main import _get_module

modules_file  = os.path.join(
    os.path.dirname(os.path.realpath('{}/..'.format(__file__))), 'constructors.json')

with open(modules_file) as fileneco:
    modules_dict = json.loads(fileneco.read())

modules_list = []

for module_label, module_class in modules_dict.items():
    modules_list.append((module_label, module_class))


@pytest.mark.parametrize("test_input,expected_class", modules_list)
def test_load_module(test_input, expected_class):
    assert _get_module(test_input).__name__ == expected_class.split('.')[-1]
