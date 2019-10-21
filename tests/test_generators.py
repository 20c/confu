import pytest
import json
from confu.generator import ConfigGenerator, generate
from tests.schemas import Schema_02


def test_generate_config():
    generator = ConfigGenerator()
    config = generator.generate(Schema_02())
    print(json.dumps(config, indent=2))
    assert config == json.loads(
        '{"int_attr": 123, "nested": {"int_attr": null}, "list_attr": [], "str_attr": "test", "str_attr_null": null}'
    )


@pytest.mark.parametrize("generator", [None, ConfigGenerator()])
def test_generate_config_shortcut(generator):
    config = generate(Schema_02(), generator)
    assert config == json.loads(
        '{"int_attr": 123, "nested": {"int_attr": null}, "list_attr": [], "str_attr": "test", "str_attr_null": null}'
    )
