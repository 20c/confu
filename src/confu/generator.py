"""
Schema to data generators
"""
from confu.schema import Attribute, Schema
from typing import Any
from typing import List
from typing import Union
from confu.generator import ConfigGenerator
from tests.schemas import Schema_02
from typing import Dict
from typing import Optional


class ConfigGenerator:
    """
    Generate config from schema using default values
    """

    def __init__(self) -> None:
        pass

    def generate(self, schema: Any) -> Union[List, int]:

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


def generate(schema: Schema_02, generator: Optional[ConfigGenerator] = None) -> Dict[str, Any]:
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
