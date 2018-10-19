import os
import six
import collections

from inspect import isclass

from confu.exceptions import ValidationError, ValidationWarning
from confu.util import config_parser_dict

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class Attribute(object):

    """
    Base confu schema attribute. All other schema attributes
    should extend this
    """


    def __init__(self, name="", **kwargs):
        # attribute name in the schema
        self.name = name

        # the default value to use, if specified a value is
        # not required in the config, other wise empty values
        # will raise a validation error during validation
        #
        # can be a function
        self.default_handler = kwargs.get("default")

        # deprecated in version
        self.deprecated = kwargs.get("deprecated")

        # added in version
        self.added = kwargs.get("added")

        # removed in version
        self.removed = kwargs.get("removed")

        # list of choices for value, if not empty values will
        # be validated against the choices in this list.
        self.choices_handler = kwargs.get("choices",[])

        # help text describing the attribute
        self.help =  kwargs.get("help","")

        self.cli_toggle = kwargs.get("cli", True)

        self.container = None


    @property
    def default(self):
        """
        Return the default value for this attribute
        """
        default = getattr(self, "default_handler", None)
        if callable(default):
            return default(self)
        return default

    @property
    def choices(self):
        """
        Return a list of possible value choices for this attribute

        Will return an empty list if the attribute is NOT limited by
        choices
        """

        choices_handler = getattr(self, "choices_handler", None)

        if callable(choices_handler):
            return self.choices_handler(self)
        return choices_handler

    @property
    def cli(self):
        return getattr(self, "cli_toggle", True)

    def validate(self, value, path, **kwargs):
        """
        Validate a value for this attribute

        Will raise a ValidationError or ValidationWarning exception on
        validation failure

        Arguments:
            - value <mixed>: the value to validate
            - path <list>: current path in the config schema, this is mostly
                used to identify where an error occured when validating
                against config data, you can pass an empty list to it when
                calling this manually
        """

        if not self.container and not self.name:
            raise ValidationError(self, path, value, "attribute at top level defined without a name")

        if self.choices_handler:
            if value not in self.choices:
                raise ValidationError(self, path, value, "invalid choice")
        return value



class Str(Attribute):

    """
    Attribute that requires a string value
    """

    def validate(self, value, path, **kwargs):
        if not isinstance(value, six.string_types):
            raise ValidationError(self, path, value, "string expected")
        return super(Str, self).validate(value, path, **kwargs)


class File(Str):
    """
    Attribute that requires a file to exist at path
    """

    def validate(self, value, path, **kwargs):
        value = super(File, self).validate(value, path, **kwargs)

        # make sure env vars get expanded
        value = os.path.expandvars(value)

        valid = (os.path.exists(value) and not os.path.isdir(value))
        if not valid:
            raise ValidationError(self, path, value, "file does not exist")

        return value


class Directory(Str):

    """
    Attribute that requires an existing directory path

    Keyword Arguments:
        - create <octal>: if set, instead of raising a ValidationError
            on a non-existing directory, attempt to create directory first
            using the value passed as mode (chmod)

            e.g., create=0o777
    """

    def __init__(self, name="", **kwargs):
        super(Directory, self).__init__(name=name, **kwargs)

        self.create = kwargs.get("create")

    def makedir(self, value, config_path):
        try:
            os.mkdir(value, self.create)
        except Exception as err:
            raise ValidationError(self, config_path, value,
                                  "tried to create directory  but failed with error" \
                                  ": {}".format(err))

    def validate(self, value, path, **kwargs):
        value = super(Directory, self).validate(value,
                                                         path, **kwargs)

        # make sure env vars get expanded
        value = os.path.expandvars(value)

        if self.create is not None and not os.path.exists(value):
            self.makedir(value, path)

        valid = (os.path.exists(value) and os.path.isdir(value))
        if not valid:
            raise ValidationError(self, path, value, "valid path to directory expected")

        return value


class Bool(Attribute):
    """
    Attribute that requires a boolean value
    """

    true_values = ["true","yes","1"]
    false_values = ["false","no","0"]

    def validate(self, value, path, **kwargs):
        if isinstance(value, str):
            if value.lower() in self.true_values:
                value = True
            elif value.lower() in self.false_values:
                value = False
            else:
                raise ValidationError(self, path, value, "boolean expected")
        return super(Bool,self).validate(bool(value), path, **kwargs)

    def finalize_click(self, param, name):
        del param["type"]
        return "{}/--no-{}".format(name, name.strip("-"))


    def finalize_argparse(self, param, name):
        del param["type"]
        if not self.default:
            param.update(action="store_true")
        else:
            param.update(action="store_false")
            name = "--no-{}".format(name.strip("-"))
        return name

class Int(Attribute):

    """
    Attribute that requires an integer value
    """

    def validate(self, value, path, **kwargs):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "integer expected")
        return super(Int, self).validate(value, path, **kwargs)


class Float(Attribute):

    """
    Attribute that requires a float value
    """

    def validate(self, value, path, **kwargs):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "float expected")
        return super(Float, self).validate(value, path, **kwargs)


class List(Attribute):

    """
    Attribute that requires a list value
    """

    def __init__(self, name, item, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = []

        if isclass(item):
            kwargs["cli"] = False

        if isinstance(item, Attribute):
            item.container = self

        super(List, self).__init__(name, **kwargs)

        if not isinstance(item, Attribute):
            raise TypeError("item needs to be a confu attribute")

        self.item = item


    @property
    def cli(self):
        if isinstance(self.item, Schema):
            return False
        return super(List, self).cli


    def validate(self, value, path, **kwargs):

        if isinstance(value, str):
            value = value.split(",")

        if not isinstance(value, list):
            raise ValidationError(self, path, value, "list expected")

        idx = 0
        for item in value:
            try:
                value[idx] = self.item.validate(item, path+[idx])
                idx += 1
            except ValidationError as error:
                kwargs.get("errors", ValidationErrorProcessor()).error(error)
            except ValidationWarning as warning:
                kwargs.get("warnings", ValidationErrorProcessor()).warning(warning)
        return super(List, self).validate(value, path, **kwargs)

class ValidationErrorProcessor(object):
    """
    This the default validation error processor, it will raise an exception
    when a warning or error is encountered
    """
    def error(self, error):
        raise error
    def warning(self, warning):
        raise warning

class CollectValidationExceptions(ValidationErrorProcessor):
    """
    This validation error processor will store all errors and warnings it encounters
    and NOT raise any exceptions
    """
    def __init__(self):
        self.exceptions = []
    def __iter__(self):
        for exc in self.exceptions:
            yield exc
    def __len__(self):
        return len(self.exceptions)
    def __getitem__(self, key):
        return self.exceptions[key]
    def error(self, error):
        self.exceptions.append(error)
    def warning(self, warning):
        self.exceptions.append(warning)

class Schema(Attribute):

    def __init__(self, *args, **kwargs):
        # collect attributes
        self._attr = {}
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Attribute):
                self._attr[name] = attr

        if "default" not in kwargs:
            kwargs["default"] = {}

        kwargs["cli"] = False

        self.item = kwargs.get("item")
        if self.item and self._attr:
            raise ValueError("You cannot specify an `item` attribute on a " \
                             "Schema instance that has attributes defined within")
        elif self.item:
            self.item.container = self

        super(Schema, self).__init__(*args, **kwargs)



    def attributes(self):
        # redundant?
        for name, attr in self._attr.items():
            yield (name, attr)


    def walk(self, callback, path=None):
        if not path:
            path = []
        for name, attribute in self.attributes():
            if isinstance(attribute, Schema):
                callback(attribute, path+[name])
                attribute.walk(callback, path=path+[name])
            else:
                callback(attribute, path+[name])


    def validate(self, config, path=None, errors=None, warnings=None):

        """
        Validate config data against this schema

        Attributes:
            - config <dict>

        Keyword Attributes:
            - path <list>: current path in the config data, this can be
                ignored on the initial call and will be set automatically
                on any subsequent calls (sub schemas)
            - errors <ValidationErrorProcessor>
            - warnigns <ValidationErrorProcessor>
        """

        if path is None:
            path = []
        if errors is None:
            errors = ValidationErrorProcessor()
        if warnings is None:
            warnings = ValidationErrorProcessor()

        # munge Config support without having to import munge
        if isinstance(config, collections.MutableMapping) and hasattr(config, "data"):
            config = config.data
        elif isinstance(config, configparser.ConfigParser):
            config = config_parser_dict(config)

        if not isinstance(config, dict):
            return errors.error(ValidationError(path[-1], path, config, "dictionary expected"))

        for key, value in config.items():
            try:
                attribute = self._attr.get(key, self.item)

                if attribute is None:
                    raise ValidationWarning(key, path, value, "unknown attribute '{}'".format(key))
                else:
                    config[key] = attribute.validate(value, path+[key], errors=errors, warnings=warnings)
            except ValidationError as error:
                errors.error(error)
            except ValidationWarning as warning:
                warnings.warning(warning)

        for name, attribute in self.attributes():
            if name not in config and getattr(attribute, "default_handler", None) is None:
                errors.error(ValidationError(attribute, path+[name], None, "missing"))

        return config


class Dict(Schema):
    """
    Wrapper for schema with arbitrary keys
    """
    def __init__(self, name, item, *args, **kwargs):
        return super(Dict, self).__init__(name=name, item=item, *args, **kwargs)


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

    def validate(self, config, path=None, errors=None, warnings=None):
        """
        call validate on the schema returned by self.schema
        """
        return self.schema(config).validate(config, path=path, errors=errors, warnings=warnings)



def validate(schema, config, raise_errors=False, log=None, **kwargs):
    """
    Helper function that allows schema validation to either collect or raise errors

    Arguments:
        - schema <Schema>: schema instance
        - config <dict|munge.Config>

    Keyword Arguments:
        - raise_errors <bool=False>: if True will raise a ValidationError exception
            if it encounters validation errors

            If False it will instead collect errors and warnings and return a tuple:

            success<bool>, errors<CollectValidationExceptions>, warnings<CollectValidationException>
        - log <callable>: function to use to log errors, will be passed
            a str message

        - any additional kwargs will be passed on to Schema.validate
    """

    if raise_errors:
        schema.validate(config, **kwargs)

    else:
        errors = CollectValidationExceptions()
        warnings = CollectValidationExceptions()
        schema.validate(config, errors=errors, warnings=warnings, **kwargs)

        success = len(errors) == 0

        if log and callable(log):
            for error in errors:
                log("[Config Error] {}".format(error.pretty))
            for warning in warnings:
                log("[Config Warning] {}".format(warning.pretty))
            if not success:
                log("{} errors, {} warnings in config".format(len(errors), len(warnings)))

        return (success, errors, warnings)



def apply_default(config, attribute, path):
    """
    Apply attribute default to config dict at the specified path

    Arguments:
        - config <dict>: the config dictonary
        - attribute <Attribute>: attribute instance
        - path <list<str>>: full path of the attribute in the schema
    """

    _config = config
    prev = None

    for section in path:
        prev = _config
        _config = _config.get(section)

    if _config is None and attribute.default_handler is not None:
        prev[section] = attribute.default


def apply_defaults(schema, config):
    """
    Take a config object and apply a schema's default values to keys that
    are missing.

    Arguments:
        - schema <Schema>: schema instance
        - config <dict>: the config dictonary
    """

    def callback(attribute, path):
        apply_default(config, attribute, path)
    schema.walk(callback)
