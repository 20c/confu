from confu.schema import Schema, ProxySchema, List, Int, Float, Bool, Str


class NestedSchema_01(Schema):
    int_attr = Int("int_attr")


class NestedSchema_02(Schema):
    int_attr = Int("int_attr")
    int_attr_choices = Int(
        "int_attr_choices", choices=[1, 2, 3], default=1, help="This can be 1,2 or 3"
    )


class Schema_01(Schema):
    int_attr = Int("int_attr")
    str_attr = Str("str_attr")
    list_attr = List("list_attr", NestedSchema_01())
    nested = NestedSchema_01("nested")


class Schema_02(Schema):
    int_attr = Int("int_attr", default=123)
    str_attr = Str("str_attr", default="test")
    list_attr = List(item=NestedSchema_01())
    str_attr_null = Str(default=None)
    nested = NestedSchema_01("nested")


class Schema_03(Schema):
    int_attr = Int("int_attr", default=123, help="an integer attribute")
    str_attr = Str("str_attr", default="test", help="a unicode attribute")
    bool_attr = Bool("bool_attr", help="a boolean attribute")
    bool_attr_w_dflt = Bool(
        "bool_attr_w_dflt", default=False, help="a boolean attribute"
    )
    bool_attr_w_dflt_yes = Bool(
        "bool_attr_w_dflt_yes", default=True, help="a boolean attribute"
    )
    float_attr = Float("float_attr", default=1.23, help="a float attribute")
    list_attr_int = List("list_attr_int", Int("list_attr_int_item"))
    list_attr_str = List("list_attr_str", Str("list_attr_str_item"))
    list_attr_schema = List(name="list_attr_schema", item=NestedSchema_01())
    nested = NestedSchema_02("nested")
    int_attr_disabled = Int("int_attr_disabled", cli=False)
    int_attr_fntgl_on = Int(cli=lambda x: True, default=1)
    int_attr_fntgl_off = Int(cli=lambda x: False, default=1)


class Schema_04(Schema):
    int_attr = Int("int_attr", default=123)
    str_attr = Str("str_attr", default="test")
    str_attr_null = Str(default=None)
    list_attr = List("list_attr", NestedSchema_01())
    list_attr_w_default = List("list_attr_w_default", item=Int(), default=[1, 2, 3])
    nested = NestedSchema_02("nested")


class Schema_05(Schema):
    name = Str("name")


class ProxySchema_01(ProxySchema):
    def schema(self, config):
        if "name" in config:
            return Schema_05()
        return Schema_01()


class ProxySchema_02(ProxySchema):
    def schema(self, config):
        return Schema_07()


class Schema_06(Schema):
    proxies = List("proxies", ProxySchema_01())


class Schema_07(Schema):
    str_attr = Str(default="test123")
    str_attr_null = Str(default=None)
    int_attr = Int(default=123)
    str_attr_nd = Str()


class Schema_08(Schema):
    dict_attr = Schema("dict_attr", item=Schema_07())
    str_attr_nd = Str("str_attr_nd")


class Schema_09(Schema):
    list_attr_schema = List("list_attr", item=Schema_07())
    list_attr_dict = List("list_attr_dict", item=Schema(item=Schema_07()))


class Schema_10(Schema):
    dict_attr = Schema("dict_attr", item=Schema_08())
    list_of_dicts = List("list_of_dicts", item=Schema(item=Schema_07()))
    list_of_dicts2 = List("list_of_dicts2", item=Schema(item=Schema_08()))
    list_of_schemas = List("list_of_schemas", item=Schema_07())
    deep_list = List("deep_list", item=Schema_09())
    schema_attr = Schema_07()


class Schema_11(Schema):
    list_attr = List("list_attr", item=List("", item=Schema(item=Schema_07())))


class Schema_12(Schema):
    proxies = List("proxies", ProxySchema_02())
    proxies_dict = Schema("proxies_dict", item=Schema(item=ProxySchema_02()))
    proxy = ProxySchema_02()


class Schema_13(Schema):
    int_attr = Int()
    str_attr = Str()
