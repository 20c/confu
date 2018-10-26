import os
import pytest
import json
from .schemas import (Schema_01, Schema_04, Schema_10, Schema_11)
from confu.schema import (apply_default, apply_defaults)

def test_schema_attributes():
    schema = Schema_01()
    attributes = [attr for attr in schema.attributes()]
    for name, attribute in attributes:
        assert attribute == schema._attr.get(name)

def test_schema_walk():
    paths = []
    def callback(attribute,path):
        paths.append(".".join(path))
    Schema_01().walk(callback)
    assert sorted(paths) == sorted(['int_attr', 'list_attr', 'nested', 'nested.int_attr', 'str_attr'])


@pytest.mark.parametrize("SchemaClass,config,expected", [
    (Schema_04, {},
        {"int_attr":123, "str_attr":"test", "list_attr":[],
        "list_attr_w_default":[1,2,3], "nested":{"int_attr_choices":1}}),

    (Schema_04, {"int_attr":999},
        {"int_attr":999, "str_attr":"test", "list_attr":[],
         "list_attr_w_default":[1,2,3], "nested":{"int_attr_choices":1}}),

    (Schema_04, {"nested":{"int_attr":1}},
        {"int_attr":123, "str_attr":"test", "list_attr":[],
         "list_attr_w_default":[1,2,3],
         "nested":{"int_attr_choices":1,"int_attr":1}}),

    (Schema_04, {"nested":{"int_attr":1, "int_attr_choices":2}},
        {"int_attr":123, "str_attr":"test", "list_attr":[],
         "list_attr_w_default":[1,2,3],
         "nested":{"int_attr_choices":2,"int_attr":1}}),

    (Schema_04, {"list_attr_w_default":[4,5,6]},
        {"int_attr":123, "str_attr":"test", "list_attr":[],
         "list_attr_w_default":[4,5,6],
         "nested":{"int_attr_choices":1}}),

    (Schema_10, "in.01.json", "expected.01.json"),
    (Schema_11, "in.02.json", "expected.02.json"),
    (Schema_10, "in.03.json", "expected.03.json"),
])
def test_apply_defaults(SchemaClass, config, expected):
    if not isinstance(config, dict):
        with open(os.path.join(os.path.dirname(__file__),"data","defaults",config)) as fh:
            config = json.load(fh)
    if not isinstance(expected, dict):
        with open(os.path.join(os.path.dirname(__file__),"data","defaults",expected)) as fh:
            expected = json.load(fh)
    apply_defaults(SchemaClass(), config)
    print(json.dumps(config, indent=2))
    print(json.dumps(expected, indent=2))
    assert expected == config
