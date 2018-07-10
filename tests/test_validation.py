import os
import json
import pytest
from confu.exceptions import *
from confu.schema import (
    Schema,
    ListAttribute,
    IntAttribute,
    FloatAttribute,
    BoolAttribute,
    StringAttribute,
    DirectoryAttribute,
    CollectValidationExceptions
)

from .schemas import (
    Schema_01,
)


basedir = os.path.join(os.path.dirname(__file__))


@pytest.mark.parametrize("AttributeClass,value_pass,validated,value_fail,init", [
    (StringAttribute, "test", "test", 123,{}),
    (IntAttribute, 123, 123, "test",{}),
    (FloatAttribute, 1.23, 1.23, "test",{}),
    (BoolAttribute, True, True, "test",{}),
    (BoolAttribute, "True", True, "test",{}),
    (BoolAttribute, "yes", True, "test",{}),
    (BoolAttribute, "1", True, "test",{}),
    (BoolAttribute, 1, True, "test",{}),
    (BoolAttribute, False, False, "test",{}),
    (BoolAttribute, "False", False, "test",{}),
    (BoolAttribute, "no", False, "test",{}),
    (BoolAttribute, "0", False, "test",{}),
    (BoolAttribute, 0, False, "test",{}),
    (DirectoryAttribute, os.path.join(basedir, "data"), os.path.join(basedir, "data"), 123,{}),
    (ListAttribute, [1,2,3], [1,2,3], "test", {"item":IntAttribute("test")}),
    (ListAttribute, [1,2,3], [1,2,3], ["test"], {"item":IntAttribute("test")})
])
def test_attribute(AttributeClass, value_pass, validated, value_fail, init):
    attribute = AttributeClass("test", **init)
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
     ValidationError(None, ["int_attr"], None, "missing"))
])
def test_schema(SchemaClass, config_pass, config_fail, error):
    with open(os.path.join(os.path.dirname(__file__),"data",config_pass)) as fh:
        config = json.load(fh)
    SchemaClass.validate(config)
    with open(os.path.join(os.path.dirname(__file__),"data",config_fail)) as fh:
        config = json.load(fh)
    with pytest.raises(ValidationError) as exception_info:
        SchemaClass.validate(config)

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
    SchemaClass.validate(config, errors=errors)

    assert errors[0] == error
