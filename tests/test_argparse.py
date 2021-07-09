import argparse
import json
import os

import pytest

from confu.cli import apply_argparse, argparse_options
from confu.config import Config
from tests.schemas import Schema_02, Schema_03, Schema_10, Schema_15


def test_argparse():

    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_03())

    parsed = parser.parse_args([])

    assert parsed.nested__int_attr_choices == 1
    assert parsed.nested__int_attr is None
    assert parsed.list_attr_str == []
    assert parsed.list_attr_int == []
    assert parsed.str_attr == "test"
    assert parsed.int_attr == 123
    assert parsed.float_attr == 1.23
    assert parsed.bool_attr is None
    assert parsed.bool_attr_w_dflt is False
    assert parsed.bool_attr_w_dflt_yes is True
    assert parsed.int_attr_fntgl_on == 1
    assert getattr(parsed, "list_attr_schema", None) is None

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
    assert parsed.bool_attr is True

    parsed = parser.parse_args(["--bool-attr-w-dflt"])
    assert parsed.bool_attr_w_dflt is True

    parsed = parser.parse_args(["--no-bool-attr-w-dflt-yes"])
    assert parsed.bool_attr_w_dflt_yes is False

    with pytest.raises(SystemExit):
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
    assert parsed.bool_attr is None
    assert parsed.bool_attr_w_dflt is False
    assert parsed.bool_attr_w_dflt_yes is True
    assert getattr(parsed, "list_attr_schema", None) is None
    assert getattr(parsed, "int_attr_disabled", None) is None


def test_argparse_filter_attributes():

    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_03(), attributes=["str_attr", "nested__int_attr"])

    parsed = parser.parse_args([])

    assert parsed.str_attr == "test"
    assert parsed.nested__int_attr is None
    assert getattr(parsed, "float_attr", None) is None
    assert getattr(parsed, "bool_attr", None) is None
    assert getattr(parsed, "list_attr_str", None) is None
    assert getattr(parsed, "list_attr_int", None) is None
    assert getattr(parsed, "int_attr", None) is None
    assert getattr(parsed, "nested__int_attr_choices", None) is None


def test_argparse_no_default_from_schema():
    """
    Instead of taking defaults from schema, we default
    to False. Default overrides are still valid.
    """
    parser = argparse.ArgumentParser()
    defaults = {
        "str_attr": "test dynamic",
        "nested": {"int_attr_choices": 2, "int_attr": 3},
    }

    argparse_options(parser, Schema_03(), defaults, default_from_schema=False)

    parsed = parser.parse_args([])

    assert parsed.nested__int_attr_choices == 2
    assert parsed.nested__int_attr == 3
    assert parsed.list_attr_str is None
    assert parsed.list_attr_int is None
    assert parsed.str_attr == "test dynamic"
    assert parsed.int_attr is None
    assert parsed.float_attr is None
    assert parsed.bool_attr is None
    assert parsed.bool_attr_w_dflt is None
    assert parsed.bool_attr_w_dflt_yes is None


def test_argparse_default_config():
    """
    Here we override defaults from a config file.
    """
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data/argparse/config.json"
    )
    with open(path) as file:
        config = json.load(file)

    parser = argparse.ArgumentParser()
    argparse_options(parser, Schema_02(), config)

    parsed = parser.parse_args([])

    assert parsed.str_attr == "hello world"
    assert parsed.int_attr == 234
    assert parsed.str_attr_null is None

    parsed = parser.parse_args(
        ["--str-attr", "donkey", "--int-attr", "345", "--str-attr-null", "yoyo"]
    )
    assert parsed.str_attr == "donkey"
    assert parsed.int_attr == 345
    assert parsed.str_attr_null == "yoyo"


def test_apply_argparse_03():
    """
    Test of the apply_argparse function for Schema 03.
    Two nested schema options are passed to the config.
    """
    config = Config(Schema_03())
    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, Schema_03())

    args = parser.parse_args(
        [
            "--str-attr",
            "donkey",
            "--list-attr-int",
            "1,2,3",
            "--list-attr-str",
            "1,2,3",
            "--int-attr",
            "999",
            "--float-attr",
            "365.2",
            "--bool-attr",
            "--bool-attr-w-dflt",
            "--no-bool-attr-w-dflt-yes",
            "--nested.int-attr-choices",
            "2",
            "--nested.int-attr",
            "3",
        ]
    )

    config = apply_argparse(args, config)

    # Config should be overwritten by arguments
    assert config["str_attr"] == "donkey"
    assert config["list_attr_int"] == [1, 2, 3]
    assert config["list_attr_str"] == ["1", "2", "3"]
    assert config["int_attr"] == 999
    assert config["bool_attr"] is True
    assert config["bool_attr_w_dflt"] is True
    assert config["bool_attr_w_dflt_yes"] is False
    assert config["nested"]["int_attr_choices"] == 2
    assert config["nested"]["int_attr"] == 3


def test_apply_argparse_03_invalid():
    """
    Test of the apply_argparse function for Schema 03.
    Here we provide additional attributes outside of the schema.
    These should be marked as invalid.
    """
    config = Config(Schema_03())
    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, Schema_03())

    parser.add_argument("--new-attribute-int", type=int)
    parser.add_argument("--new-attribute-str", type=str)

    args = parser.parse_args(
        [
            "--new-attribute-int",
            "123",
            "--new-attribute-str",
            "not good",
        ]
    )

    config = apply_argparse(args, config)

    # New arguments should not get added to config
    assert not config.get("new_attribute_int", False)
    assert not config.get("new_attribute_str", False)


def test_apply_argparse_10():
    """
    Test of the apply_argparse function for Schema 10.
    Four nested schema options are passed to the config.
    """
    schema_10 = Schema_10()
    with open(
        os.path.join(os.path.dirname(__file__), "data", "defaults", "in.01.json")
    ) as fh:
        config_data = json.load(fh)

    config = Config(schema_10, config_data)

    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, schema_10)

    args = parser.parse_args(
        [
            "--schema-attr.int-attr",
            "2222",
            "--schema-attr.str-attr",
            "hello world",
            "--schema-attr.str-attr-nd",
            "defaults empty string",
            "--schema-attr.str-attr-null",
            "not null",
        ]
    )

    apply_argparse(args, config)

    # Config should be overwritten by arguments
    assert config["schema_attr"]["int_attr"] == 2222
    assert config["schema_attr"]["str_attr"] == "hello world"
    assert config["schema_attr"]["str_attr_nd"] == "defaults empty string"
    assert config["schema_attr"]["str_attr_null"] == "not null"


def test_apply_argparse_10_invalid():
    """
    Test of the apply_argparse function for Schema 10.
    Four nested schema options are passed to the config.
    """
    schema_10 = Schema_10()
    with open(
        os.path.join(os.path.dirname(__file__), "data", "defaults", "in.01.json")
    ) as fh:
        config_data = json.load(fh)

    config = Config(schema_10, config_data)

    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, schema_10)

    parser.add_argument("--schema-attr.new-attr-int", type=int)
    parser.add_argument("--schema-attr.new-attr-str", type=str)

    args = parser.parse_args(
        [
            "--schema-attr.new-attr-int",
            "2222",
            "--schema-attr.new-attr-str",
            "hello world",
        ]
    )

    apply_argparse(args, config)

    # New arguments should not get added to config
    assert not config["schema_attr"].get("new_attribute_int", False)
    assert not config["schema_attr"].get("new_attribute_str", False)


def test_apply_argparse_15():
    """
    Test of the apply_argparse function for Schema 15.
    Here we have a doubly nested override.
    """
    schema_15 = Schema_15()

    config = Config(schema_15)

    parser = argparse.ArgumentParser("new-parser")
    argparse_options(parser, schema_15)

    args = parser.parse_args(
        [
            "--nested-schema.float-attr",
            "9.87",
            "--nested-schema.schema-attr.int-attr",
            "90210",
            "--nested-schema.schema-attr.str-attr",
            "updated",
        ]
    )
    apply_argparse(args, config)

    # Config should be overwritten by arguments
    assert config["nested_schema"]["float_attr"] == 9.87
    assert config["nested_schema"]["schema_attr"]["int_attr"] == 90210
    assert config["nested_schema"]["schema_attr"]["str_attr"] == "updated"
