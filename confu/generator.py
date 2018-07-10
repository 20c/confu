from inspect import isclass
from confu.schema import (
    Schema,
    Attribute
)


class ConfigGenerator(object):
    def __init__(self):
        pass

    def generate(self, schema):
        if isclass(schema) and issubclass(schema, Schema):
            config = {}
            for name in dir(schema):
                attribute = getattr(schema,name)
                if isinstance(attribute, Attribute) or (isclass(attribute) and issubclass(attribute, Schema)):
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
    """
    if not generator:
        generator = ConfigGenerator()
    return generator.generate(schema)
