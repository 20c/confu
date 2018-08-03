import pytest
from .schemas import Schema_01

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
    assert sorted(paths) == sorted(['int_attr', 'list_attr', 'nested.int_attr', 'str_attr'])
