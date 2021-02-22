import configparser
import os

import pytest

from confu.util import _set_bool, _set_option, config_parser_dict, set_bool, set_option


def test_config_parser_dict():
    path = os.path.join(os.path.dirname(__file__), "data", "configparse.cfg")
    config = configparser.ConfigParser()
    config.read(path)

    assert config_parser_dict(config) == {"test": {"a": "test"}}


def test_set_option_wrapper():
    assert "TEST_SETTING" not in globals()
    set_option("TEST_SETTING", "world")
    assert globals()["TEST_SETTING"] == "world"


def test_set_option():
    context = {}
    _set_option("TEST_SETTING", "hello", context)
    assert context["TEST_SETTING"] == "hello"


def test_set_option_w_env_var():
    """
    Environment variables take precedence over provided options
    """
    context = {}
    os.environ["TEST_SETTING"] = "world"
    _set_option("TEST_SETTING", "hello", context)
    assert context["TEST_SETTING"] == "world"


def test_set_option_coerce_env_var():
    """
    We coerce the environment variable to the same type
    as the provided default.
    """
    context = {}
    # env variables can never be set as integers
    os.environ["TEST_SETTING"] = "123"

    # setting an option with a default integer will coerce the env
    # variable as well (fix for issue #888)
    _set_option("TEST_SETTING", 321, context)
    assert context["TEST_SETTING"] == 123

    # setting an option with a default string will coerce the env
    # variable as well
    _set_option("TEST_SETTING", "321", context)
    assert context["TEST_SETTING"] == "123"

    _set_option("TEST_SETTING", 123.1, context)
    assert context["TEST_SETTING"] == 123.0


def test_set_option_booleans():

    context = {}
    # env variables can only be set as strings
    os.environ["TEST_SETTING"] = "False"

    # setting the option with a boolean
    # will use set_bool to handle the
    # type coercion of the env variable
    _set_option("TEST_SETTING", False, context)
    assert context["TEST_SETTING"] is False

    # the environment variable has precedence
    _set_option("TEST_SETTING", True, context)
    assert context["TEST_SETTING"] is False

    del os.environ["TEST_SETTING"]
    del context["TEST_SETTING"]
    _set_option("TEST_SETTING", True, context)
    # We can set boolean values without env vars as well
    assert context["TEST_SETTING"] is True


def test_set_bool_wrapper():
    assert "TEST_SETTING" not in globals()
    set_bool("TEST_SETTING", False)
    assert globals()["TEST_SETTING"] is False


def test_set_bool():
    """
    We coerce the environment variable to a boolean
    """
    context = {}

    # 0 is interpreted as False
    os.environ["TEST_SETTING"] = "0"
    # env variables can never be set as integers
    _set_bool("TEST_SETTING", False, context)
    assert context["TEST_SETTING"] is False

    # the environment variable has precedence
    _set_bool("TEST_SETTING", True, context)
    assert context["TEST_SETTING"] is False

    # We raise an error if the env variable
    # cannot be reasonably coerced to a bool

    os.environ["TEST_SETTING"] = "100"
    with pytest.raises(ValueError):
        _set_option("TEST_SETTING", True, context)


def test_set_options_none():
    """
    We coerce the environment variable to a boolean
    """
    context = {}

    # 0 is interpreted as False
    os.environ["TEST_SETTING"] = "0"

    # setting an option with None without setting the
    # envvar_type raises an error
    with pytest.raises(ValueError):
        _set_option("TEST_SETTING", None, context)

    # setting an option with None but setting the
    # envvar_type is fine
    _set_option("TEST_SETTING", None, context, envvar_type=int)
    assert context["TEST_SETTING"] == 0

    _set_option("TEST_SETTING", None, context, envvar_type=str)
    assert context["TEST_SETTING"] == "0"
