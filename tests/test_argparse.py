import pytest
import argparse
import json
import os

from tests.schemas import Schema_02, Schema_03, Schema_10


from confu.cli import argparse_options, apply_argparse
from confu.config import Config
from confu.schema import apply_default, apply_defaults, ApplyDefaultError

def test_argparse():

    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_03())

    parsed = parser.parse_args([])

    assert parsed.nested__int_attr_choices == 1
    assert parsed.nested__int_attr == None
    assert parsed.list_attr_str == []
    assert parsed.list_attr_int == []
    assert parsed.str_attr == "test"
    assert parsed.int_attr == 123
    assert parsed.float_attr == 1.23
    assert parsed.bool_attr == None
    assert parsed.bool_attr_w_dflt == False
    assert parsed.bool_attr_w_dflt_yes == True
    assert parsed.int_attr_fntgl_on == 1
    assert getattr(parsed, "list_attr_schema", None) == None

    with pytest.raises(AttributeError):
        assert parsed.int_attr_disabled == 1

    with pytest.raises(AttributeError):
        assert parsed.int_attr_fntgl_off == 1

    parsed = parser.parse_args(["--nested.int-attr-choices", "2"])
    assert parsed.nested__int_attr_choices == 2

    parsed = parser.parse_args(["--nested.int-attr", "3"])
    assert parsed.nested__int_attr == 3

    parsed = parser.parse_args(["--str-attr", "donkey"])
    assert parsed.str_attr == "donkey"

    parsed = parser.parse_args(["--list-attr-int", "1,2,3"])
    assert parsed.list_attr_int == [1, 2, 3]

    parsed = parser.parse_args(["--list-attr-str", "1,2,3"])
    assert parsed.list_attr_str == ["1", "2", "3"]

    parsed = parser.parse_args(["--int-attr", "999"])
    assert parsed.int_attr == 999

    parsed = parser.parse_args(["--bool-attr"])
    assert parsed.bool_attr == True

    parsed = parser.parse_args(["--bool-attr-w-dflt"])
    assert parsed.bool_attr_w_dflt == True

    parsed = parser.parse_args(["--no-bool-attr-w-dflt-yes"])
    assert parsed.bool_attr_w_dflt_yes == False

    with pytest.raises(SystemExit) as exc:
        parsed = parser.parse_args(["--nested.int-attr-choices", "4"])


def test_argparse_dynamic_defaults():

    defaults = {
        "str_attr": "test dynamic",
        "nested": {"int_attr_choices": 2, "int_attr": 3},
    }

    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_03(), defaults)

    parsed = parser.parse_args([])

    assert parsed.nested__int_attr_choices == 2
    assert parsed.nested__int_attr == 3
    assert parsed.list_attr_str == []
    assert parsed.list_attr_int == []
    assert parsed.str_attr == "test dynamic"
    assert parsed.int_attr == 123
    assert parsed.float_attr == 1.23
    assert parsed.bool_attr == None
    assert parsed.bool_attr_w_dflt == False
    assert parsed.bool_attr_w_dflt_yes == True
    assert getattr(parsed, "list_attr_schema", None) == None
    assert getattr(parsed, "int_attr_disabled", None) == None


def test_argparse_filter_attributes():

    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_03(), attributes=["str_attr", "nested__int_attr"])

    parsed = parser.parse_args([])

    assert parsed.str_attr == "test"
    assert parsed.nested__int_attr == None
    assert getattr(parsed, "float_attr", None) == None
    assert getattr(parsed, "bool_attr", None) == None
    assert getattr(parsed, "list_attr_str", None) == None
    assert getattr(parsed, "list_attr_int", None) == None
    assert getattr(parsed, "int_attr", None) == None
    assert getattr(parsed, "nested__int_attr_choices", None) == None


def test_argparse_default_config():
    import os
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/argparse/config.json"
    )
    with open(path, "r") as file:
        config = json.load(file)

    # Create argparser WITH config
    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_02(), config)

    parsed = parser.parse_args([])

    assert parsed.str_attr == "hello world"
    assert parsed.int_attr == 234
    assert parsed.str_attr_null == None

    parsed = parser.parse_args(
        ["--str-attr", "donkey", "--int-attr", "345", "--str-attr-null", "yoyo"]
    )
    assert parsed.str_attr == "donkey"
    assert parsed.int_attr == 345
    assert parsed.str_attr_null == "yoyo"


def test_apply_argparse_03():
    config = Config(Schema_03())
    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, Schema_03())

    args = parser.parse_args([
        "--str-attr", "donkey",
        "--list-attr-int", "1,2,3",
        "--list-attr-str", "1,2,3",
        "--int-attr", "999",
        "--float-attr", "365.2",
        "--bool-attr",
        "--bool-attr-w-dflt",
        "--no-bool-attr-w-dflt-yes",
        "--nested.int-attr-choices", "2",
        "--nested.int-attr", "3",
    ])

    config = apply_argparse(args, config) 

    # Overwritten by arguments
    assert config["str_attr"] == "donkey"
    assert config["list_attr_int"] == [1, 2, 3]
    assert config["list_attr_str"] == ["1", "2", "3"]
    assert config["int_attr"] == 999
    assert config["bool_attr"] == True
    assert config["bool_attr_w_dflt"] == True
    assert config["bool_attr_w_dflt_yes"] == False
    assert config["nested"]["int_attr_choices"] == 2
    assert config["nested"]["int_attr"] == 3

def test_apply_argparse_10():
    with open(
            os.path.join(os.path.dirname(__file__), "data", "defaults", "in.01.json")
        ) as fh:
            config_data = json.load(fh)
    with open(
            os.path.join(os.path.dirname(__file__), "data", "defaults", "expected.01.json")
        ) as fh:
            expected = json.load(fh)
    
    config = Config(Schema_10(), config_data)

    from pprint import pprint
    pprint(config.data)
    
    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, Schema_10())

    args = parser.parse_args([
        "--schema-attr.int-attr", "999",
        "--schema-attr.str-attr", "hello world",
        "--schema-attr.str-attr-nd", "defaults empty string",
        "--schema-attr.str-attr-null", "not null",
    ])
    config = apply_argparse(args, config) 

    # Overwritten by arguments
    config["schema_attr"]["int_attr"] == 999
    config["schema_attr"]["str_attr"] = "hello world"
    config["schema_attr"]["str_attr_nd"] = "defaults empty string"
    config["schema_attr"]["str_attr_null"] = "not null"

    print(parser.parse_args(["-h"]))
    assert 0