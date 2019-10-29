"""
Schema to data generators
"""
from confu.schema import Schema, Attribute


class ConfigGenerator(object):
    """
    Generate config from schema using default values
    """

    def __init__(self):
        pass

    def generate(self, schema):

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


def generate(schema, generator=None):
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
