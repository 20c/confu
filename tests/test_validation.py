import os
import json
import pytest
from confu.exceptions import *
from confu.schema import (
    Schema,
    ProxySchema,
    List,
    Int,
    Float,
    Bool,
    Str,
    Directory,
    CollectValidationExceptions
)

from .schemas import (
    Schema_01,
    Schema_05,
    Schema_06
)


basedir = os.path.join(os.path.dirname(__file__))


@pytest.mark.parametrize("Class,value_pass,validated,value_fail,init", [
    (Str, "test", "test", 123,{}),
    (Int, 123, 123, "test",{}),
    (Float, 1.23, 1.23, "test",{}),
    (Bool, True, True, "test",{}),
    (Bool, "True", True, "test",{}),
    (Bool, "yes", True, "test",{}),
    (Bool, "1", True, "test",{}),
    (Bool, 1, True, "test",{}),
    (Bool, False, False, "test",{}),
    (Bool, "False", False, "test",{}),
    (Bool, "no", False, "test",{}),
    (Bool, "0", False, "test",{}),
    (Bool, 0, False, "test",{}),
    (Directory, os.path.join(basedir, "data"), os.path.join(basedir, "data"), 123,{}),
    (List, [1,2,3], [1,2,3], "test", {"item":Int("test")}),
    (List, [1,2,3], [1,2,3], ["test"], {"item":Int("test")})
])
def test_attribute(Class, value_pass, validated, value_fail, init):
    attribute = Class("test", **init)
    assert attribute.validate(value_pass, []) == validated
    with pytest.raises(ValidationError):
        attribute.validate(value_fail, [])

@pytest.mark.parametrize("SchemaClass,config_pass,config_fail,error", [
    (Schema_01, "nesting/success.json", "nesting/failure01.json",
     ValidationError(None, ["nested", "int_attr"], "test", "integer expected")),
    (Schema_01, "nesting/success.json", "nesting/failure02.json",
     ValidationError(None, ["nested"], [1,2,3], "dictionary expected")),
    (Schema_01, "nesting/success.json", "nesting/failure03.json",
     ValidationError(None, ["list_attr",0], 1, "dictionary expected")),
    (Schema_01, "nesting/success.json", "nesting/failure04.json",
     ValidationError(None, ["int_attr"], None, "missing")),
    (Schema_06, "nesting/proxy_success.json", "nesting/proxy_failure01.json",
     ValidationError(None, ["proxies", 0, "int_attr"], None, "missing"))
])
def test_schema(SchemaClass, config_pass, config_fail, error):
    schema = SchemaClass()
    with open(os.path.join(os.path.dirname(__file__),"data",config_pass)) as fh:
        config = json.load(fh)
    schema.validate(config)
    with open(os.path.join(os.path.dirname(__file__),"data",config_fail)) as fh:
        config = json.load(fh)
    with pytest.raises(ValidationError) as exception_info:
        schema.validate(config)

    assert exception_info.value == error


@pytest.mark.parametrize("SchemaClass,config_fail,error", [
    (Schema_01,"nesting/failure01.json",
     ValidationError(None, ["nested", "int_attr"], "test", "integer expected")),
    (Schema_01,"nesting/failure02.json",
     ValidationError(None, ["nested"], [1,2,3], "dictionary expected")),
    (Schema_01,"nesting/failure03.json",
     ValidationError(None, ["list_attr",0], 1, "dictionary expected"))
])
def test_schema_collect_exc(SchemaClass, config_fail, error):
    with open(os.path.join(os.path.dirname(__file__),"data",config_fail)) as fh:
        config = json.load(fh)

    errors = CollectValidationExceptions()
    schema = SchemaClass()
    schema.validate(config, errors=errors)

    assert errors[0] == error


def test_attr_name_validation():

    attr = Str()
    with pytest.raises(ValidationError) as exception_info:
        attr.validate("test", [])

    item = Str()
    attr = List("list", item)
    assert item.container == attr
    assert attr.validate(["test"], []) == ["test"]

def test_attr_name_same_as_property_name():
    Schema_05().validate({"name":"test"})

