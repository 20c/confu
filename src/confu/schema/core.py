"""
Fundamental schema attributes

These can be imported directly from `confu.schema`
"""
from __future__ import annotations

import collections.abc
import configparser
import copy
import os
from inspect import isclass
from typing import Any, Callable, Iterator, NoReturn

import munge

from confu import types
from confu.exceptions import ApplyDefaultError, ValidationError, ValidationWarning
from confu.util import config_parser_dict


class Attribute:

    """
    Base confu schema attribute. All other schema attributes
    should extend this

    """

    def __init__(self, name: str = "", **kwargs: Any) -> None:

        """
        Initialize attribute

        **Keyword Arguments**

        - name (`str`): describes the attribute name, if not specified
          explicitly will be set through the schema that instantiates
          the attribute.
        - default (`mixed`): the default value of this attribute. Once a default
          value is set, schema validation will no longer raise a
          validation error if the attribute is missing from the
          configuration.
        - choices (`list`): if specified on values in this list may be set
          for this attribute
        - help (`str`): help description
        - cli (`bool=True|function`): enable CLI support for this attribute
        - deprecated (`str`): version id of when this attribute will be deprecated
        - added (`str`): version id of when this attribute was added to the schema
        - removed (`str`): version id of when this attribute will be removed
        """

        # attribute name in the schema
        self.name = name

        # the default value to use, if specified a value is
        # not required in the config, other wise empty values
        # will raise a validation error during validation
        #
        # can be a function

        if "default" in kwargs:
            self.default_handler = kwargs.get("default")

        # deprecated in version
        self.deprecated = kwargs.get("deprecated")

        # added in version
        self.added = kwargs.get("added")

        # removed in version
        self.removed = kwargs.get("removed")

        # list of choices for value, if not empty values will
        # be validated against the choices in this list.
        self.choices_handler = kwargs.get("choices", [])

        # help text describing the attribute
        self.help = kwargs.get("help", "")

        # include this attribute when generating cli attributes
        self.cli_toggle = kwargs.get("cli", True)

        # show default value in cli help text
        self.cli_show_default = kwargs.get("cli_show_default", True)

        self.container = None

    @property
    def has_default(self) -> bool:
        return hasattr(self, "default_handler")

    @property
    def default_is_none(self) -> bool:
        return self.has_default and self.default is None

    @property
    def default(self) -> Any:
        """
        Return the default value for this attribute
        """
        default = getattr(self, "default_handler", None)
        if callable(default):
            return default(self)
        return default

    @property
    def choices(self) -> Any:
        """
        Return a list of possible value choices for this attribute

        Will return an empty list if the attribute is **NOT** limited by
        choices
        """

        choices_handler = getattr(self, "choices_handler", None)

        if callable(choices_handler):
            return self.choices_handler(self)
        return choices_handler

    @property
    def cli(self) -> bool:
        """
        Returns whether or not the attribute is available
        in as a cli argument  when confu is used to generated
        argparse or click arguments
        """

        toggle = getattr(self, "cli_toggle", True)
        if callable(toggle):
            return toggle(self)
        return toggle

    def validate(self, value: Any, path: list[str], **kwargs: Any) -> Any:
        """
        Validate a value for this attribute

        Will raise a `ValidationError` or `ValidationWarning` exception on
        validation failure

        **Arguments**

        - value (`mixed`): the value to validate
        - path (`list`): current path in the config schema, this is mostly
          used to identify where an error occured when validating
          against config data, you can pass an empty list to it when
          calling this manually
        """

        if not self.container and not self.name:
            raise ValidationError(
                self, path, value, "attribute at top level defined without a name"
            )

        if self.choices_handler:
            if value not in self.choices:
                raise ValidationError(self, path, value, "invalid choice")
        return value


class Str(Attribute):

    """
    Attribute that requires a string value

    Keyword Attributes:
        - blank <bool=False>: if True allow "" as a value
    """

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)
        self.blank = kwargs.get("blank", False)
        if not self.blank and self.default_is_blank:
            self.blank = True

    @property
    def default_is_blank(self) -> bool:
        return self.default == ""

    def validate(
        self,
        value: str | None,
        path: list[str],
        **kwargs: Any,
    ) -> str | None:
        if not isinstance(value, str) and not self.default_is_none:
            raise ValidationError(self, path, value, "string expected")

        if value == "" and not self.blank:
            raise ValidationError(self, path, value, "cannot be blank")

        return super().validate(value, path, **kwargs)


class File(Str):
    """
    Attribute that requires a file to exist at path

    **Keyword Attributes**

    - require_exist ('bool=True'): if `True` file needs to exist
    """

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)
        self.require_exist = kwargs.get("require_exist", True)

    def validate(self, value: str | None, path: list[str], **kwargs: Any) -> str | None:
        value = super().validate(value, path, **kwargs)

        if value is None and self.default_is_none:
            return value

        if value == "" and self.blank:
            return value

        # make sure env vars get expanded
        value = os.path.expandvars(value)

        # make sure user vars get expanded
        value = os.path.expanduser(value)

        # expand to absolute path
        value = os.path.abspath(value)

        valid = (os.path.exists(value) or not self.require_exist) and not os.path.isdir(
            value
        )
        if not valid:
            raise ValidationError(self, path, value, "file does not exist")

        return value


class Directory(Str):

    """
    Attribute that requires an existing directory path

    **Keyword Arguments**

    - require_exist ('bool=True'): if `True` directory needs to exist
    - create (`octal`): if set, instead of raising a ValidationError
    on a non-existing directory, attempt to create directory first
    using the value passed as mode (chmod) e.g., create=0o777
    """

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)

        self.create = kwargs.get("create")
        self.require_exist = kwargs.get("require_exist", True)

    def makedir(self, value: str, config_path: list[str]) -> None:
        try:
            os.makedirs(value, self.create)
        except Exception as err:
            raise ValidationError(
                self,
                config_path,
                value,
                "tried to create directory  but failed with error" ": {}".format(err),
            )

    def validate(self, value: str | None, path: list[str], **kwargs: Any) -> str | None:
        value = super().validate(value, path, **kwargs)

        if value is None and self.default_is_none:
            return value

        # make sure env vars get expanded
        value = os.path.expandvars(value)

        # if value is blank, and validation was not caught by `blank` validation
        # of Str we forfeit validation and it is assume that the application
        # will validate manually once the path is set.
        if value == "":
            return value

        # make sure user vars get expanded
        value = os.path.expanduser(value)

        # expand to absolute path
        value = os.path.abspath(value)

        if self.create is not None and not os.path.exists(value):
            self.makedir(value, path)

        if self.require_exist:
            valid = os.path.exists(value) and os.path.isdir(value)
        else:
            valid = True

        if not valid:
            raise ValidationError(
                self, path, value, f"valid path to directory expected: {value}"
            )

        return value


class Bool(Attribute):
    """
    Attribute that requires a boolean value
    """

    true_values = ["true", "yes", "1"]
    false_values = ["false", "no", "0"]

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)
        self.cli_show_default = False

    def validate(self, value: int | str, path: list[str], **kwargs: Any) -> bool:
        if isinstance(value, str):
            if value.lower() in self.true_values:
                value = True
            elif value.lower() in self.false_values:
                value = False
            else:
                raise ValidationError(self, path, value, "boolean expected")
        return super().validate(bool(value), path, **kwargs)

    def finalize_click(self, param: dict[str, Any], name: str) -> str:
        del param["type"]
        return "{}/--no-{}".format(name, name.strip("-"))

    def finalize_argparse(self, param: dict[str, Any], name: str) -> str:
        del param["type"]
        if not param["default"]:
            param.update(action="store_true")
        else:
            param.update(action="store_false")
            if param.get("help"):
                param["help"] = "DISABLE {}".format(param["help"])
            name = "--no-{}".format(name.strip("-"))
        return name


class Int(Attribute):

    """
    Attribute that requires an integer value
    """

    def validate(
        self,
        value: int | str | None,
        path: list[str],
        **kwargs: Any,
    ) -> int | None:
        if value is None and self.default_is_none:
            return value
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "integer expected")
        return super().validate(value, path, **kwargs)


class Float(Attribute):

    """
    Attribute that requires a float value
    """

    def validate(
        self, value: float | str | None, path: list[str], **kwargs: Any
    ) -> float | None:
        if value is None and self.default_is_none:
            return value
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "float expected")
        return super().validate(value, path, **kwargs)


class TimeDuration(Attribute):

    """
    Attribute that requires an TimeDuration type value.
    TimeDuration is defined in `confu.types`
    """

    def validate(
        self,
        value: types.TimeDuration | float | str | None,
        path: list[str],
        **kwargs: Any,
    ) -> TimeDuration:
        if value is None and self.default_is_none:
            return value
        try:
            value = types.TimeDuration(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "TimeDuration expected")
        return super().validate(value, path, **kwargs)

    @property
    def default(self) -> TimeDuration | None:
        default = super().default
        if default is None:
            return None
        else:
            return types.TimeDuration(default)

    @property
    def choices(self) -> list:
        return list(map(types.TimeDuration, super().choices))


class List(Attribute):

    """
    Attribute that requires a list value
    """

    # TODO: item should be a required positional argument, but
    # doing so means flipping the order with name, which breaks
    # peoples schemas (major version fix?)

    def __init__(
        self,
        name: str | None = None,
        item: Attribute | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize List attribute

        **Keyword Arguments**

        - name (`str`): describes the attribute name, if not specified
          explicitly will be set through the schema that instantiates
          the attribute.
        - item (`Attribute`): allows you to specify an arbitrary attribute
          to use for all values in the list.
        - default (`mixed`): the default value of this attribute. Once a default
          value is set, schema validation will no longer raise a
          validation error if the attribute is missing from the
          configuration.
        - help (`str`): help description
        - cli (`bool=True`): enable CLI support for this attribute
        - deprecated (`str`): version id of when this attribute will be deprecated
        - added (`str`): version id of when this attribute was added to the schema
        - removed (`str`): version id of when this attribute will be removed
        """

        if not isinstance(item, Attribute):
            raise TypeError("item needs to be a confu attribute")

        if "default" not in kwargs:
            kwargs["default"] = []

        if isclass(item):
            kwargs["cli"] = False

        if isinstance(item, Attribute):
            item.container = self

        super().__init__(name, **kwargs)

        self.item = item

    @property
    def cli(self) -> bool:
        if isinstance(self.item, Schema):
            return False
        return super().cli

    def validate(
        self,
        value: list | str,
        path: list[str],
        **kwargs: Any,
    ) -> Any:

        if isinstance(value, str):
            value = value.split(",")

        if not isinstance(value, list):
            raise ValidationError(self, path, value, "list expected")

        errors = kwargs.get("errors", ValidationErrorProcessor())
        warnings = kwargs.get("warnings", ValidationErrorProcessor())

        validated = []
        idx = 0
        for item in value:
            try:
                if isinstance(self.item, Schema):
                    validated.append(
                        self.item.validate(
                            item, path + [idx], errors=errors, warnings=warnings
                        )
                    )
                else:
                    validated.append(self.item.validate(item, path + [idx]))
                idx += 1
            except ValidationError as error:
                errors.error(error)
            except ValidationWarning as warning:
                warnings.warning(warning)
        return super().validate(validated, path, **kwargs)


class ValidationErrorProcessor:
    """
    This the default validation error processor, it will raise an exception
    when a warning or error is encountered
    """

    def error(self, error: ValidationError) -> NoReturn:
        raise error

    def warning(self, warning):
        raise warning


class CollectValidationExceptions(ValidationErrorProcessor):
    """
    This validation error processor will store all errors and warnings it encounters
    and NOT raise any exceptions
    """

    def __init__(self) -> None:
        self.exceptions = []

    def __iter__(self):
        yield from self.exceptions

    def __len__(self) -> int:
        return len(self.exceptions)

    def __getitem__(self, key: int) -> ValidationError:
        return self.exceptions[key]

    def error(self, error: ValidationError) -> None:
        self.exceptions.append(error)

    def warning(self, warning: ValidationWarning) -> None:
        self.exceptions.append(warning)


class Schema(Attribute):

    """
    Describes a confu schema.

    Instantiate confu attributes as properties of the schema.

    As the schema itself is a confu attribute, you may nest schemas
    within schemas

    **Example**

    ```
    class MySchema(Schema):
        str_attr = Str()
    ```
    """

    def __init__(self, *args: str, **kwargs: Any) -> None:
        """
        Initialize schema

        **Keyword Arguments**

        - item (`Attribute`): allows you to specify an arbitrary attribute
          to use for all values in the schema. This is only allowed if your
          schema does **NOT** explicitly set any attributes in it's definition
        - name (`str`): describes the attribute name, if not specified
          explicitly will be set through the schema that instantiates
          the attribute.
        - default (`mixed`): the default value of this attribute. Once a default
          value is set, schema validation will no longer raise a
          validation error if the attribute is missing from the
          configuration.
        - help (`str`): help description
        - cli (`bool=True`): enable CLI support for this attribute
        - deprecated (`str`): version id of when this attribute will be deprecated
        - added (`str`): version id of when this attribute was added to the schema
        - removed (`str`): version id of when this attribute will be removed
        """

        # collect attributes
        self._attr = {}
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Attribute):
                self._attr[name] = attr
                if not attr.name:
                    attr.name = name

        if "default" not in kwargs:
            kwargs["default"] = {}

        kwargs["cli"] = False

        self.item = kwargs.get("item")
        if self.item and self._attr:
            raise ValueError(
                "You cannot specify an `item` attribute on a "
                "Schema instance that has attributes defined within"
            )
        elif self.item:
            self.item.container = self

        super().__init__(*args, **kwargs)

    def attributes(self) -> Iterator:
        # redundant?
        yield from list(self._attr.items())

    def walk(self, callback: Callable, path: list[str] | None = None) -> None:
        if not path:
            path = []
        for name, attribute in self.attributes():
            if isinstance(attribute, Schema):
                callback(attribute, path + [name])
                attribute.walk(callback, path=path + [name])
            else:
                callback(attribute, path + [name])

    def validate(
        self,
        config: dict,
        path: list[str] | None = None,
        errors: ValidationErrorProcessor | None = None,
        warnings: ValidationErrorProcessor | None = None,
    ) -> dict[str, Any]:

        """
        Validate config data against this schema

        **Attributes**

        - config (`dict`): config to validate

        **Keyword Attributes**

        - path (`list`): current path in the config data, this can be
          ignored on the initial call and will be set automatically
          on any subsequent calls (nested schemas)
        - errors (`ValidationErrorProcessor`)
        - warnigns (`ValidationErrorProcessor`)
        """

        if path is None:
            path = []
        if errors is None:
            errors = ValidationErrorProcessor()
        if warnings is None:
            warnings = ValidationErrorProcessor()

        # munge Config support without having to import munge
        if isinstance(config, collections.abc.MutableMapping) and hasattr(
            config, "data"
        ):
            config = config.data
        elif isinstance(config, configparser.ConfigParser):
            config = config_parser_dict(config)

        if not isinstance(config, dict):
            return errors.error(
                ValidationError(path[-1], path, config, "dictionary expected")
            )

        for key, value in list(config.items()):
            try:
                attribute = self._attr.get(key, self.item)

                if attribute is None:
                    raise ValidationWarning(
                        key, path, value, f"unknown attribute '{key}'"
                    )
                else:
                    config[key] = attribute.validate(
                        value, path + [key], errors=errors, warnings=warnings
                    )
            except ValidationError as error:
                errors.error(error)
            except ValidationWarning as warning:
                warnings.warning(warning)

        for name, attribute in self.attributes():
            if name not in config and not attribute.has_default:
                errors.error(ValidationError(attribute, path + [name], None, "missing"))

        return config


class Dict(Schema):
    """
    Wrapper for schema with arbitrary keys

    For this the `item` property needs to be set.
    """

    def __init__(
        self,
        name: str | None = None,
        item: Int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, item=item, *args, **kwargs)


class ProxySchema(Schema):

    """
    An object that can be used in place of a schema in order to
    dynamically obtain a schema instance from somewhere else during
    validate
    """

    def schema(self, config):
        """
        return a schema instance
        """
        raise NotImplementedError()

    def validate(
        self,
        config: dict,
        path: list[str] | None = None,
        errors: ValidationErrorProcessor | None = None,
        warnings: ValidationErrorProcessor | None = None,
    ) -> dict:
        """
        call validate on the schema returned by self.schema
        """
        return self.schema(config).validate(
            config, path=path, errors=errors, warnings=warnings
        )


def validate(
    schema: Schema,
    config: dict | munge.Config,
    raise_errors: bool = False,
    log: Callable | None = None,
    **kwargs: Any,
) -> tuple[bool, CollectValidationExceptions, CollectValidationExceptions] | None:
    """
    Helper function that allows schema validation to either collect or raise errors

    **Arguments**

    - schema (`Schema`): schema instance
    - config (`dict|munge.Config`)

    **Keyword Arguments**

    - raise_errors (`bool=False`): if `True` will raise a ValidationError exception
      if it encounters validation errors

      If `False` it will instead collect errors and warnings and return a tuple:

      ```
      success(bool), errors(CollectValidationExceptions), warnings(CollectValidationException)
      ```

    - log (`callable`): function to use to log errors, will be passed
      a str message
    - any additional kwargs will be passed on to `Schema.validate`
    """

    warnings = CollectValidationExceptions()
    if raise_errors:
        schema.validate(config, warnings=warnings, **kwargs)
        return (True, [], warnings)
    else:
        errors = CollectValidationExceptions()
        schema.validate(config, errors=errors, warnings=warnings, **kwargs)

        num_errors = len(errors)
        num_warnings = len(warnings)

        success = num_errors == 0

        if log and callable(log):
            for error in errors:
                log(f"[Config Error] {error.pretty}")
            for warning in warnings:
                log(f"[Config Warning] {warning.pretty}")
            if not success:
                log(f"{num_errors} errors, {num_warnings} warnings in config")

        return (success, errors, warnings)


def apply_default(config: dict, attribute: Attribute, path: list[str]) -> None:
    """
    Apply attribute default to config dict at the specified path

    **Arguments**

    - config (`dict`): the config dictonary
    - attribute (`Attribute`): attribute instance
    - path (`list(str)`): full path of the attribute in the schema
    """

    _config = config
    prev = None

    for section in path:
        prev = _config
        _config = _config.get(section)

    if isinstance(attribute, List):

        # attribute is a List, need to handle items
        # accordingly
        if _config and isinstance(attribute.item, Schema):

            # list is holding schemas, apply defaults
            # to each item in the list
            for item in _config:
                apply_defaults(attribute.item, item, debug=True)

        if _config and isinstance(attribute.item, List):

            # list is holding lists, apply defaults
            # to each item in the list
            for item in _config:
                apply_default(item, attribute.item, [])

        elif _config is None and attribute.has_default:

            # list is holding normal attribute, set default
            # value
            prev[section] = attribute.default

    elif isinstance(attribute, Schema):

        # attribute is a Schema

        if isinstance(attribute, ProxySchema):
            attribute = attribute.schema(_config)

        if (
            _config
            and isinstance(attribute.item, List)
            and isinstance(attribute.item.item, Schema)
        ):
            # schema with arbitrary keys
            # holding lists holding schemas
            # TODO: find a cleaner way to handle this case

            for k, item in list(_config.items()):
                apply_default(_config, attribute.item, [k])

        if _config is None:
            prev[section] = copy.deepcopy(attribute.default or {})

        if attribute.item is None:
            apply_defaults(attribute, prev[section])
        if isinstance(attribute.item, Schema):
            apply_defaults(attribute.item, prev[section])

    elif _config is None and attribute.has_default:
        prev[section] = attribute.default


def apply_defaults(schema: Schema, config: dict, debug: bool = False) -> None:
    """
    Take a config object and apply a schema's default values to keys that
    are missing.

    **Arguments**

    - schema (`Schema`): schema instance
    - config (`dict`): the config dictonary
    """

    if isinstance(schema, ProxySchema):
        # schema is proxy schema, retrieve actual schema
        # before proceeding
        schema = schema.schema(config)

    if isinstance(schema.item, Schema):
        # schema has arbitrary keys holding another schema
        for k, v in list(config.items()):
            apply_defaults(schema.item, v, debug=debug)
        return
    elif isinstance(schema.item, List):
        # schema has arbitrary keys holding a list
        for k, v in list(config.items()):
            apply_default(config, schema.item, [k])
        return

    # normal schema, walk it's attributes and apply defaults
    def callback(attribute: Any, path: list[str]) -> None:
        try:
            apply_default(config, attribute, path)
        except Exception as exc:
            raise ApplyDefaultError(attribute, path, None, exc)

    schema.walk(callback)
