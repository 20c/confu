from confu.schema import (
    Schema,
    ListAttribute,
    IntAttribute,
    FloatAttribute,
    BoolAttribute,
    StringAttribute
)

class NestedSchema_01(Schema):
    int_attr = IntAttribute("int_attr")

class NestedSchema_02(Schema):
    int_attr = IntAttribute("int_attr")
    int_attr_choices = IntAttribute("int_attr_choices", choices=[1,2,3], default=1, help="This can be 1,2 or 3")

class Schema_01(Schema):
    int_attr = IntAttribute("int_attr")
    str_attr = StringAttribute("str_attr")
    list_attr = ListAttribute("list_attr", NestedSchema_01)
    nested = NestedSchema_01

class Schema_02(Schema):
    int_attr = IntAttribute("int_attr", default=123)
    str_attr = StringAttribute("str_attr", default="test")
    list_attr = ListAttribute("list_attr", NestedSchema_01)
    nested = NestedSchema_01

class Schema_03(Schema):
    int_attr = IntAttribute("int_attr", default=123, help="an integer attribute")
    str_attr = StringAttribute("str_attr", default="test", help="a unicode attribute")
    bool_attr = BoolAttribute("bool_attr", help="a boolean attribute")
    bool_attr_w_dflt = BoolAttribute("bool_attr_w_dflt", default=False, help="a boolean attribute")
    bool_attr_w_dflt_yes = BoolAttribute("bool_attr_w_dflt_yes", default=True, help="a boolean attribute")
    float_attr = FloatAttribute("float_attr", default=1.23, help="a float attribute")
    list_attr_int = ListAttribute("list_attr_int", IntAttribute("list_attr_int_item"))
    list_attr_str = ListAttribute("list_attr_str", StringAttribute("list_attr_str_item"))
    list_attr_schema = ListAttribute("list_attr_schema", NestedSchema_01)
    nested = NestedSchema_02
    int_attr_disabled = IntAttribute("int_attr_disabled", cli=False)
