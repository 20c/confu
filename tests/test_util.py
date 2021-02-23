import configparser
import os

import pytest

from confu.util import SettingsManager, config_parser_dict


@pytest.fixture()
def globals_fixture():
    # Setup
    g = globals()
    yield g
    # Teardown
    del g["TEST_SETTING"]


@pytest.fixture()
def envvar_fixture():
    # Setup
    os.environ["TEST_SETTING"] = "world"
    yield
    # Teardown
    if os.environ.get("TEST_SETTING"):
        del os.environ["TEST_SETTING"]


def test_config_parser_dict():
    path = os.path.join(os.path.dirname(__file__), "data", "configparse.cfg")
    config = configparser.ConfigParser()
    config.read(path)

    assert config_parser_dict(config) == {"test": {"a": "test"}}


def test_set_option_global(globals_fixture):
    g = globals_fixture
    settings = SettingsManager(g)
    settings.set_option("TEST_SETTING", "world")
    assert g["TEST_SETTING"] == "world"


def test_settings_manager():
    scope = {}
    settings = SettingsManager(scope)
    assert settings.scope == scope


def test_set_from_env(envvar_fixture):
    scope = {}
    settings = SettingsManager(scope)
    settings.set_from_env("TEST_SETTING")
    assert scope["TEST_SETTING"] == "world"


def test_set_from_env_no_env_no_default():
    scope = {}
    settings = SettingsManager(scope)
    assert os.environ.get("TEST_SETTING") is None
    settings.set_from_env("TEST_SETTING")
    assert scope.get("TEST_SETTING") is None


def test_set_from_env_no_env_w_default():
    scope = {}
    settings = SettingsManager(scope)
    assert os.environ.get("TEST_SETTING") is None
    settings.set_from_env("TEST_SETTING", default="default")
    assert scope["TEST_SETTING"] == "default"


def test_set_option():
    scope = {}
    settings = SettingsManager(scope)
    settings.set_option("TEST_SETTING", "hello")
    assert scope["TEST_SETTING"] == "hello"


def test_set_option_w_env_var(envvar_fixture):
    """
    Environment variables take precedence over provided options
    """
    scope = {}
    settings = SettingsManager(scope)
    settings.set_option("TEST_SETTING", "hello")
    assert scope["TEST_SETTING"] == "world"


def test_set_option_coerce_env_var(envvar_fixture):
    """
    We coerce the environment variable to the same type
    as the provided default.
    """
    scope = {}
    settings = SettingsManager(scope)
    # env variables can never be set as integers
    os.environ["TEST_SETTING"] = "123"

    # setting an option with a default integer will coerce the env
    # variable as well (fix for issue #888)

    settings.set_option("TEST_SETTING", 321)
    assert scope["TEST_SETTING"] == 123

    # setting an option with a default string will coerce the env
    # variable as well
    settings.set_option("TEST_SETTING", "321")
    assert scope["TEST_SETTING"] == "123"

    settings.set_option("TEST_SETTING", 123.1)
    assert scope["TEST_SETTING"] == 123.0


def test_set_option_booleans(envvar_fixture):

    scope = {}
    settings = SettingsManager(scope)
    # env variables can only be set as strings
    os.environ["TEST_SETTING"] = "False"

    # setting the option with a boolean
    # will use set_bool to handle the
    # type coercion of the env variable
    settings.set_option("TEST_SETTING", False)
    assert scope["TEST_SETTING"] is False

    # the environment variable has precedence
    settings.set_option("TEST_SETTING", True)
    assert scope["TEST_SETTING"] is False

    del os.environ["TEST_SETTING"]
    del scope["TEST_SETTING"]
    settings.set_option("TEST_SETTING", True)
    # We can set boolean values without env vars as well
    assert scope["TEST_SETTING"] is True


def test_set_bool_global(globals_fixture):
    g = globals_fixture
    settings = SettingsManager(g)

    assert "TEST_SETTING" not in g
    settings.set_bool("TEST_SETTING", False)
    assert g["TEST_SETTING"] is False


def test_set_bool(envvar_fixture):
    """
    We coerce the environment variable to a boolean
    """
    scope = {}
    settings = SettingsManager(scope)
    # 0 is interpreted as False
    os.environ["TEST_SETTING"] = "0"
    # env variables can never be set as integers
    settings.set_bool("TEST_SETTING", False)
    assert scope["TEST_SETTING"] is False

    # the environment variable has precedence
    settings.set_bool("TEST_SETTING", True)
    assert scope["TEST_SETTING"] is False

    # We raise an error if the env variable
    # cannot be reasonably coerced to a bool

    os.environ["TEST_SETTING"] = "100"
    with pytest.raises(ValueError):
        settings.set_bool("TEST_SETTING", True)


def test_set_options_none(envvar_fixture):
    """
    We coerce the environment variable to a boolean
    """
    scope = {}
    settings = SettingsManager(scope)
    # 0 is interpreted as False
    os.environ["TEST_SETTING"] = "0"

    # setting an option with None without setting the
    # envvar_type raises an error
    with pytest.raises(ValueError):
        settings.set_option(
            "TEST_SETTING",
            None,
        )

    # setting an option with None but setting the
    # envvar_type is fine
    settings.set_option("TEST_SETTING", None, envvar_type=int)
    assert scope["TEST_SETTING"] == 0

    settings.set_option("TEST_SETTING", None, envvar_type=str)
    assert scope["TEST_SETTING"] == "0"
