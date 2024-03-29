import pytest

from confu.schema import Bool, Directory, Float, Int, List, Schema, Str, TimeDuration


@pytest.mark.parametrize("Class", [Str, Int, Float, Bool, Directory])
def test_init(Class):
    """
    test attribute initiation
    """
    attribute = Class("test", help="test attribute")
    assert attribute.name == "test"
    assert attribute.help == "test attribute"


@pytest.mark.parametrize(
    "Class,choices_in,choices_out",
    [
        (Str, ["a", "b"], ["a", "b"]),
        (Str, lambda x: ["a", "b"], ["a", "b"]),
        (Int, [1, 2], [1, 2]),
        (Int, lambda x: [1, 2], [1, 2]),
        (Float, [1.2, 2.3], [1.2, 2.3]),
        (Float, lambda x: [1.2, 2.3], [1.2, 2.3]),
        (TimeDuration, [" 2y 2d 2h 2m 2s 2ms", "3m", 120], [63295322.002, 180, 120]),
        (
            TimeDuration,
            lambda x: ["2y 2d 2h 2m 2s 2ms", "3m", 120],
            [63295322.002, 180, 120],
        ),
        (Directory, ["/a", "/b"], ["/a", "/b"]),
        (Directory, lambda x: ["/a", "/b"], ["/a", "/b"]),
    ],
)
def test_choices(Class, choices_in, choices_out):
    """
    test attribute choices property
    """
    attribute = Class("test", choices=choices_in)
    assert attribute.choices == choices_out


@pytest.mark.parametrize(
    "Class,default_in,default_out",
    [
        (Str, "test", "test"),
        (Str, lambda x: "test", "test"),
        (Str, None, None),
        (Int, 123, 123),
        (Int, lambda x: 123, 123),
        (Float, 1.23, 1.23),
        (Float, lambda x: 1.23, 1.23),
        (TimeDuration, "2y 2d 2h 2m 2s 2ms", 63295322.002),
        (TimeDuration, lambda x: "2y 2d 2h 2m 2s 2ms", 63295322.002),
        (TimeDuration, 180122.002, 180122.002),
        (TimeDuration, lambda x: 180122.002, 180122.002),
        (Bool, True, True),
        (Bool, lambda x: True, True),
        (Directory, "/test", "/test"),
        (Directory, lambda x: "/test", "/test"),
    ],
)
def test_default(Class, default_in, default_out):
    """
    test attribute default property
    """
    attribute = Class("test", default=default_in)
    assert attribute.default == default_out


def test_list():
    with pytest.raises(TypeError):
        attribute = List("test", 123)

    item = Int("item")
    attribute = List("test", item)
    assert attribute.item == item
    assert attribute.name == "test"

    class Item(Schema):
        test_sub = Int("test_sub")

    item = Item()
    attribute = List("test", item)
    assert attribute.item == item

    attribute = List("test", Int())
    attribute = List(item=Int())
    attribute = List(name="test", item=Int())


@pytest.mark.parametrize("Class", [Str, Int, Bool, Float, TimeDuration])
def test_none_default(Class):
    attribute = Class("test", default=None)
    assert attribute.has_default is True
    assert attribute.default is None
