import pytest
import json
from confu.generator import ConfigGenerator
from .schemas import Schema_02

def test_generate_config():
    generator = ConfigGenerator()
    config = generator.generate(Schema_02())
    assert config == json.loads('{"int_attr": 123, "nested": {"int_attr": null}, "list_attr": [], "str_attr": "test"}')
