"""
Schema to data generators
"""
from __future__ import annotations

from confu.schema import Attribute, Schema


class ConfigGenerator:
    """
    Generate config from schema using default values
    """

    def __init__(self) -> None:
        pass

    def generate(self, schema: Schema | Attribute) -> dict:

        """
        Generate confug from schema using default values

        **Arguments**

        - schema (`Schema|Attribute`): confu schema object

        **Returns**

        generated config `dict`
        """

        if isinstance(schema, Schema):
            config = {}
            for name, attribute in schema.attributes():
                config[name] = self.generate(attribute)
            return config
        elif isinstance(schema, Attribute):
            return self.generate(schema.default)
        elif isinstance(schema, list):
            return [self.generate(item) for item in schema]
        return schema


def generate(schema: Schema, generator: ConfigGenerator | None = None) -> dict:
    """
    generate config shortcut function

    **Arguments**

    - schema (`Schema`): confu schema object

    **Keyword Arguments**

    - generator (`ConfigGenerator`): generator object, if non is supplied
    will instantiate a ConfigGenerator instance itself

    **Returns**

    generated config (`dict`)
    """
    if not generator:
        generator = ConfigGenerator()
    return generator.generate(schema)
