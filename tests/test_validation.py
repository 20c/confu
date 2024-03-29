import ipaddress
import json
import os

import pytest

from confu.exceptions import ValidationError
from confu.schema import (
    Bool,
    CollectValidationExceptions,
    Dict,
    Directory,
    Email,
    File,
    Float,
    Int,
    IpAddress,
    IpNetwork,
    List,
    Schema,
    Str,
    TimeDuration,
    Url,
)
from tests.schemas import Schema_01, Schema_05, Schema_06

basedir = os.path.join(os.path.dirname(__file__))
valid_dir = os.path.join(basedir, "data")
invalid_dir = os.path.join(basedir, "does", "not", "exist")
home_dir = "~"
home_dir_expanded = os.path.expanduser(home_dir)
relative_dir = "."
absolute_dir = os.path.abspath(relative_dir)
valid_file = os.path.join(basedir, "__init__.py")
invalid_file = os.path.join(basedir, "__invalid__.py")
home_file = "~/test-expanduser"
home_file_expanded = os.path.expanduser(home_file)
relative_file = "__init__.py"
absolute_file = os.path.abspath(relative_file)
ipv4 = "127.0.0.1"
ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
ipv4_n = "10.10.0.0/24"
ipv6_n = "2001:0db8:85a3:0000:0000:8a2e:0370:7334/128"


@pytest.mark.parametrize(
    "Class,value_pass,validated,value_fail,init",
    [
        (Str, "test", "test", 123, {}),
        (Str, "test", "test", "", {}),
        (Str, "", "", 123, {"blank": True}),
        (Int, 123, 123, "test", {}),
        (Float, 1.23, 1.23, "test", {}),
        (TimeDuration, 1.23, 1.23, "test", {}),
        (TimeDuration, "2y 2d 2h 2m 2s 2ms", 63295322.002, "test", {}),
        (Bool, True, True, "test", {}),
        (Bool, "True", True, "test", {}),
        (Bool, "yes", True, "test", {}),
        (Bool, "1", True, "test", {}),
        (Bool, 1, True, "test", {}),
        (Bool, False, False, "test", {}),
        (Bool, "False", False, "test", {}),
        (Bool, "no", False, "test", {}),
        (Bool, "0", False, "test", {}),
        (Bool, 0, False, "test", {}),
        (Directory, valid_dir, valid_dir, invalid_dir, {}),
        (Directory, invalid_dir, invalid_dir, None, {"require_exist": False}),
        (Directory, relative_dir, absolute_dir, invalid_dir, {}),
        (Directory, home_dir, home_dir_expanded, invalid_dir, {}),
        (File, valid_file, valid_file, invalid_file, {}),
        (File, invalid_file, invalid_file, None, {"require_exist": False}),
        (File, home_file, home_file_expanded, None, {"require_exist": False}),
        (File, relative_file, absolute_file, None, {"require_exist": False}),
        (List, [1, 2, 3], [1, 2, 3], "test", {"item": Int("test")}),
        (List, [1, 2, 3], [1, 2, 3], ["test"], {"item": Int("test")}),
        (Dict, {"a": 123}, {"a": 123}, {"a": "b"}, {"item": Int()}),
        (Dict, {"a": "123"}, {"a": 123}, {"a": "b"}, {"item": Int()}),
        (Schema, {"a": 123}, {"a": 123}, {"a": "b"}, {"item": Int()}),
        (Schema, {"a": "123"}, {"a": 123}, {"a": "b"}, {"item": Int()}),
        (Email, "a@b.com", "a@b.com", "invalid", {}),
        (Email, "a@localhost", "a@localhost", "invalid", {}),
        (Url, "http://example.com", "http://example.com", "bla", {}),
        (Url, "https://example.com", "https://example.com", "bla", {}),
        (Url, "http://localhost", "http://localhost", "bla", {}),
        (Url, "ftp://example.com", "ftp://example.com", "bla", {}),
        (
            Url,
            "http://example.com/some/path?123",
            "http://example.com/some/path?123",
            "bla",
            {},
        ),
        (Url, "http://1.2.3.4", "http://1.2.3.4", "bla", {}),
        (
            Url,
            "http://2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "http://2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "bla",
            {},
        ),
        (
            Url,
            "http://example.com",
            "http://example.com",
            "telenet://example.com",
            {"schemes": ["http"]},
        ),
        (Url, "http://example.com", "http://example.com", "/no/scheme/and/netloc", {}),
        (Url, "http://example.com", "http://example.com", "http:///no/netloc", {}),
        (IpAddress, ipv4, ipaddress.IPv4Address(ipv4), "1.2.3", {}),
        (IpAddress, ipv6, ipaddress.IPv6Address(ipv6), "1.2.3", {}),
        (IpAddress, ipv4, ipaddress.IPv4Address(ipv4), ipv6, {"protocol": 4}),
        (IpAddress, ipv6, ipaddress.IPv6Address(ipv6), ipv4, {"protocol": 6}),
        (IpAddress, "", "", "1.2.3", {"blank": True}),
        (IpNetwork, ipv4_n, ipaddress.IPv4Network(ipv4_n), "1.2.3/24", {}),
        (IpNetwork, ipv6_n, ipaddress.IPv6Network(ipv6_n), "1.2.3/64", {}),
        (IpNetwork, ipv4_n, ipaddress.IPv4Network(ipv4_n), ipv6_n, {"protocol": 4}),
        (IpNetwork, ipv6_n, ipaddress.IPv6Network(ipv6_n), ipv4_n, {"protocol": 6}),
        (IpNetwork, "", "", "10.10.0/24", {"blank": True}),
    ],
)
def test_attribute(Class, value_pass, validated, value_fail, init):
    attribute = Class("test", **init)
    assert attribute.validate(value_pass, []) == validated
    if value_fail is not None:
        with pytest.raises(ValidationError):
            attribute.validate(value_fail, [])


@pytest.mark.parametrize(
    "SchemaClass,config_pass,config_fail,error",
    [
        (
            Schema_01,
            "nesting/success.json",
            "nesting/failure01.json",
            ValidationError(None, ["nested", "int_attr"], "test", "integer expected"),
        ),
        (
            Schema_01,
            "nesting/success.json",
            "nesting/failure02.json",
            ValidationError(None, ["nested"], [1, 2, 3], "dictionary expected"),
        ),
        (
            Schema_01,
            "nesting/success.json",
            "nesting/failure03.json",
            ValidationError(None, ["list_attr", 0], 1, "dictionary expected"),
        ),
        (
            Schema_01,
            "nesting/success.json",
            "nesting/failure04.json",
            ValidationError(None, ["int_attr"], None, "missing"),
        ),
        (
            Schema_06,
            "nesting/proxy_success.json",
            "nesting/proxy_failure01.json",
            ValidationError(None, ["proxies", 0, "int_attr"], None, "missing"),
        ),
    ],
)
def test_schema(SchemaClass, config_pass, config_fail, error):
    schema = SchemaClass()
    with open(os.path.join(os.path.dirname(__file__), "data", config_pass)) as fh:
        config = json.load(fh)
    schema.validate(config)
    with open(os.path.join(os.path.dirname(__file__), "data", config_fail)) as fh:
        config = json.load(fh)
    with pytest.raises(ValidationError) as exception_info:
        schema.validate(config)

    assert exception_info.value == error


@pytest.mark.parametrize(
    "SchemaClass,config_fail,error",
    [
        (
            Schema_01,
            "nesting/failure01.json",
            ValidationError(None, ["nested", "int_attr"], "test", "integer expected"),
        ),
        (
            Schema_01,
            "nesting/failure02.json",
            ValidationError(None, ["nested"], [1, 2, 3], "dictionary expected"),
        ),
        (
            Schema_01,
            "nesting/failure03.json",
            ValidationError(None, ["list_attr", 0], 1, "dictionary expected"),
        ),
    ],
)
def test_schema_collect_exc(SchemaClass, config_fail, error):
    with open(os.path.join(os.path.dirname(__file__), "data", config_fail)) as fh:
        config = json.load(fh)

    errors = CollectValidationExceptions()
    schema = SchemaClass()
    schema.validate(config, errors=errors)

    assert errors[0] == error


def test_attr_name_validation():

    attr = Str()
    with pytest.raises(ValidationError):
        attr.validate("test", [])

    item = Str()
    attr = List("list", item)
    assert item.container == attr
    assert attr.validate(["test"], []) == ["test"]


def test_attr_name_same_as_property_name():
    Schema_05().validate({"name": "test"})


@pytest.mark.parametrize(
    "AttributeClass", [Str, Int, Float, Directory, File, Email, IpAddress, Url]
)
def test_default_none(AttributeClass):
    attr = AttributeClass("test", default=None)
    assert attr.validate(None, []) is None


@pytest.mark.parametrize(
    "AttributeClass", [Str, Directory, File, Email, IpAddress, Url]
)
def test_infer_blank(AttributeClass):
    attr = AttributeClass("test", default="")
    assert attr.validate("", []) == ""


def test_directory_create(tmpdir):
    attr = Directory(name="test", create=0o777)
    path = os.path.join(str(tmpdir), "test")
    assert attr.validate(path, []) == path

    attr = Directory(name="test")
    path = os.path.join(str(tmpdir), "test2")
    with pytest.raises(ValidationError):
        attr.validate(path, [])

    attr = Directory(name="test", create="invalid mode")
    path = os.path.join(str(tmpdir), "test3")
    with pytest.raises(ValidationError):
        attr.validate(path, [])
