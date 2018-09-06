from confu.schema import (
    Schema,
    ProxySchema,
    List,
    Int,
    Float,
    Bool,
    Str
)

class NestedSchema_01(Schema):
    int_attr = Int("int_attr")

class NestedSchema_02(Schema):
    int_attr = Int("int_attr")
    int_attr_choices = Int("int_attr_choices", choices=[1,2,3], default=1, help="This can be 1,2 or 3")

class Schema_01(Schema):
    int_attr = Int("int_attr")
    str_attr = Str("str_attr")
    list_attr = List("list_attr", NestedSchema_01())
    nested = NestedSchema_01("nested")

class Schema_02(Schema):
    int_attr = Int("int_attr", default=123)
    str_attr = Str("str_attr", default="test")
    list_attr = List("list_attr", NestedSchema_01())
    nested = NestedSchema_01("nested")

class Schema_03(Schema):
    int_attr = Int("int_attr", default=123, help="an integer attribute")
    str_attr = Str("str_attr", default="test", help="a unicode attribute")
    bool_attr = Bool("bool_attr", help="a boolean attribute")
    bool_attr_w_dflt = Bool("bool_attr_w_dflt", default=False, help="a boolean attribute")
    bool_attr_w_dflt_yes = Bool("bool_attr_w_dflt_yes", default=True, help="a boolean attribute")
    float_attr = Float("float_attr", default=1.23, help="a float attribute")
    list_attr_int = List("list_attr_int", Int("list_attr_int_item"))
    list_attr_str = List("list_attr_str", Str("list_attr_str_item"))
    list_attr_schema = List("list_attr_schema", NestedSchema_01())
    nested = NestedSchema_02("nested")
    int_attr_disabled = Int("int_attr_disabled", cli=False)

class Schema_04(Schema):
    int_attr = Int("int_attr", default=123)
    str_attr = Str("str_attr", default="test")
    list_attr = List("list_attr", NestedSchema_01())
    list_attr_w_default = List("list_attr_w_default", Int(), default=[1,2,3])
    nested = NestedSchema_02("nested")

class Schema_05(Schema):
    name = Str("name")

class ProxySchema_01(ProxySchema):
    def schema(self, config):
        if "name" in config:
            return Schema_05()
        return Schema_01()

class Schema_06(Schema):
    proxies = List("proxies", ProxySchema_01())
