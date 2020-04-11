from confu.util import config_parser_dict
import os

try:
    import configparser
except ImportError:
    import configparser as configparser


def test_config_parser_dict():
    path = os.path.join(os.path.dirname(__file__), "data", "configparse.cfg")
    config = configparser.ConfigParser()
    config.read(path)

    assert config_parser_dict(config) == {"test": {"a": "test"}}
