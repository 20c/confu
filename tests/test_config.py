
import confu
from confu.config import Config
from .schemas import Schema_04


def test_config_init():
    cfg = Config(Schema_04())

    # check internal cache
    data = cfg.data
    assert data == cfg.data


def test_empty_config():
    cfg = Config(Schema_04())

    assert len(cfg)


def test_config_copy():
    cfg = Config(Schema_04())
    cp = cfg.copy()
    assert cfg.data == cp

    cp["updated"] = True
    assert cfg.data != cp


def test_config_mapping():
    cfg = Config(Schema_04())
    cp = cfg.copy()
    assert cfg.data == cp
    assert len(cfg) == len(cp)

    for key in cfg:
        assert cp[key] == cfg[key]
