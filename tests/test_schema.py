import pytest
from .schemas import (Schema_01, Schema_04)
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


])
def test_apply_defaults(SchemaClass, config, expected):
    apply_defaults(SchemaClass(), config)
    assert expected == config
