from confu.config import Config
from confu.schema import Int, List, Schema, Str


# declaring schema classes
class Nested_Schema(Schema):
    int_attr = Int("int_attr", default=10)
    int_attr_choices = Int(
        "int_attr_choices", choices=[1, 2, 3], default=1, help="This can be 1,2 or 3"
    )


class Example_Schema(Schema):
    int_attr = Int("int_attr", default=123)
    str_attr = Str("str_attr", default="test")
    str_attr_null = Str(default=None)
    list_attr_w_default = List("list_attr_w_default", item=Int(), default=[1, 2, 3])
    nested = Nested_Schema("nested")


class Simple_Example_Schema(Schema):
    str_attr = Str("str_attr", default="test")


# config without kwargs
cfg = Config(Example_Schema())
print(cfg.data)

# config with data and meta kwrags
cfg_kwargs = Config(
    Simple_Example_Schema(),
    data={"int_attr": 42, "list_attr": [1, 2, 3]},
    meta={"meta_attr": "meta data"},
)
print(cfg_kwargs.data)

# copy the data of a schema
cfg_copy = cfg.copy()
print(cfg_copy)

# nested schema attribute
nested_value = cfg.get_nested("nested")
print(nested_value)
nested_value = cfg.get_nested("nonexistentnested")
print(nested_value)
