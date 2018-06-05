import pytest
from .schemas import Schema_01

def test_schema_attributes():
    attributes = [attr for attr in Schema_01.attributes()]
    for name, attribute in attributes:
        assert attribute == getattr(Schema_01, name)

def test_schema_walk():
    paths = []
    def callback(attribute,path):
        paths.append(".".join(path))
    Schema_01.walk(callback)
    assert paths == ['int_attr', 'list_attr', 'nested.int_attr', 'str_attr']
