import pytest
import click
import json

from click.testing import CliRunner

from .schemas import Schema_03
from confu.cli import click_options


def test_click():
    @click.command()
    @click_options(Schema_03())
    def command(**kwargs):
        print(json.dumps(kwargs))

    runner = CliRunner()
    output = runner.invoke(command, []).output
    print(output)
    result = json.loads(output)

    print(result)
    assert result["nested__int_attr_choices"] == 1
    assert result["nested__int_attr"] == None
    assert result["list_attr_str"] == []
    assert result["list_attr_int"] == []
    assert result["str_attr"] == "test"
    assert result["int_attr"] == 123
    assert result["float_attr"] == 1.23
    assert result["bool_attr"] == None
    assert result["bool_attr_w_dflt"] == False
    assert result["bool_attr_w_dflt_yes"] == True
    assert "list_attr_schema" not in result
    assert "int_attr_disabled" not in result

    result = json.loads(runner.invoke(command, ["--nested--int-attr-choices","2"]).output)
    assert result["nested__int_attr_choices"] == 2

    result = json.loads(runner.invoke(command, ["--nested--int-attr","3"]).output)
    assert result["nested__int_attr"] == 3

    result = json.loads(runner.invoke(command, ["--str-attr","donkey"]).output)
    assert result["str_attr"] == "donkey"

    result = json.loads(runner.invoke(command, ["--list-attr-int","1,2,3"]).output)
    assert result["list_attr_int"] == [1,2,3]

    result = json.loads(runner.invoke(command, ["--list-attr-str","1,2,3"]).output)
    assert result["list_attr_str"] == ["1","2","3"]

    result = json.loads(runner.invoke(command, ["--int-attr","999"]).output)
    assert result["int_attr"] == 999

    result = json.loads(runner.invoke(command, ["--bool-attr"]).output)
    assert result["bool_attr"] == True

    result = json.loads(runner.invoke(command, ["--bool-attr-w-dflt"]).output)
    assert result["bool_attr_w_dflt"] == True

    result = json.loads(runner.invoke(command, ["--no-bool-attr-w-dflt-yes"]).output)
    assert result["bool_attr_w_dflt_yes"] == False

    result = runner.invoke(command, ["--nested-int-attr-choices", 4])
    assert result.exception

