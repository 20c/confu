import pytest

from confu.schema import (
    Schema,
    Attribute,
    UnicodeAttribute,
    IntAttribute,
    FloatAttribute,
    BoolAttribute,
    ListAttribute
)



@pytest.mark.parametrize("AttributeClass", [
    UnicodeAttribute,
    IntAttribute,
    FloatAttribute,
    BoolAttribute])
def test_init(AttributeClass):
    """
    test attribute initiation
    """
    attribute = AttributeClass("test", help="test attribute")
    assert attribute.name == "test"
    assert attribute.help == "test attribute"


@pytest.mark.parametrize("AttributeClass,choices_in,choices_out", [
    (UnicodeAttribute, ["a","b"], ["a","b"]),
    (UnicodeAttribute, lambda x: ["a","b"], ["a","b"]),
    (IntAttribute, [1,2], [1,2]),
    (IntAttribute, lambda x: [1,2], [1,2]),
    (FloatAttribute, [1.2,2.3], [1.2,2.3]),
    (FloatAttribute, lambda x: [1.2,2.3], [1.2,2.3])
])
def test_choices(AttributeClass, choices_in, choices_out):
    """
    test attribute choices property
    """
    attribute = AttributeClass("test", choices=choices_in)
    assert attribute.choices == choices_out


@pytest.mark.parametrize("AttributeClass,default_in,default_out", [
    (UnicodeAttribute, "test", "test"),
    (UnicodeAttribute, lambda x: "test", "test"),
    (IntAttribute, 123, 123),
    (IntAttribute, lambda x: 123, 123),
    (FloatAttribute, 1.23, 1.23),
    (FloatAttribute, lambda x: 1.23, 1.23),
    (BoolAttribute, True, True),
    (BoolAttribute, lambda x: True, True)
])
def test_default(AttributeClass, default_in, default_out):
    """
    test attribute default property
    """
    attribute = AttributeClass("test", default=default_in)
    assert attribute.default == default_out


def test_list():
    with pytest.raises(TypeError):
        attribute = ListAttribute("test", 123)

    item = IntAttribute("item")
    attribute = ListAttribute("test", item)
    assert attribute.item == item
    assert attribute.name == "test"

    class Item(Schema):
        test_sub = IntAttribute("test_sub")
    attribute = ListAttribute("test", Item)
    assert attribute.item == Item
