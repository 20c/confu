import pytest
import argparse
import json


from tests.schemas import Schema_03

from confu.cli import argparse_options


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
    argparse_options(parser, Schema_03(), attributes=["str_attr","nested__int_attr"])

    parsed = parser.parse_args([])

    assert parsed.str_attr == "test"
    assert parsed.nested__int_attr == None
    assert getattr(parsed, "float_attr", None) == None
    assert getattr(parsed, "bool_attr", None) == None
    assert getattr(parsed, "list_attr_str", None) == None
    assert getattr(parsed, "list_attr_int", None) == None
    assert getattr(parsed, "int_attr", None) == None
    assert getattr(parsed, "nested__int_attr_choices", None) == None

