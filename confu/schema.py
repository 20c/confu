import os
import six
import collections

from inspect import isclass
from .exceptions import ValidationError, ValidationWarning

class Attribute(object):

    """
    Base confu schema attribute. All other schema attributes
    should extend this
    """


    def __init__(self, name, **kwargs):
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

        self.cli = kwargs.get("cli", True)


    @property
    def default(self):
        """
        Return the default value for this attribute
        """
        default = self.default_handler
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

        if callable(self.choices_handler):
            return self.choices_handler(self)
        return self.choices_handler

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
        if self.choices_handler:
            if value not in self.choices:
                raise ValidationError(self, path, value, "invalid choice")
        return value



class StringAttribute(Attribute):

    """
    Attribute that requires a string value
    """

    def validate(self, value, path, **kwargs):
        if not isinstance(value, six.string_types):
            raise ValidationError(self, path, value, "string expected")
        return super(StringAttribute, self).validate(value, path, **kwargs)


class DirectoryAttribute(StringAttribute):

    """
    Attribute that requires an existing directory path
    """

    def validate(self, value, path, **kwargs):
        value = super(DirectoryAttribute, self).validate(value,
                                                         path, **kwargs)

        valid = (os.path.exists(value) and os.path.isdir(value))
        if not valid:
            raise ValidationError(self, path, value, "valid path to directory expected")

        return value


class BoolAttribute(Attribute):
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
        return super(BoolAttribute,self).validate(bool(value), path, **kwargs)

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

class IntAttribute(Attribute):

    """
    Attribute that requires an integer value
    """

    def validate(self, value, path, **kwargs):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "integer expected")
        return super(IntAttribute, self).validate(value, path, **kwargs)


class FloatAttribute(Attribute):

    """
    Attribute that requires a float value
    """

    def validate(self, value, path, **kwargs):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError(self, path, value, "float expected")
        return super(FloatAttribute, self).validate(value, path, **kwargs)


class ListAttribute(Attribute):

    """
    Attribute that requires a list value
    """

    def __init__(self, name, item, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = []

        if isclass(item):
            kwargs["cli"] = False

        super(ListAttribute, self).__init__(name, **kwargs)

        if not isinstance(item, Attribute) and not issubclass(item, Schema):
            raise TypeError("item needs to either be an Attribute instance or a schema class")

        self.item = item


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
        return super(ListAttribute, self).validate(value, path, **kwargs)

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

class Schema(object):

    @classmethod
    def attributes(cls):
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Attribute) or (isclass(attr) and issubclass(attr, Schema)):
                yield (name, attr)

    @classmethod
    def walk(cls, callback, path=None):
        if not path:
            path = []
        for name, attribute in cls.attributes():
            if isinstance(attribute, Attribute):
                callback(attribute, path+[name])
            if isclass(attribute) and issubclass(attribute, Schema):
                attribute.walk(callback, path=path+[name])


    @classmethod
    def validate(cls, config, path=None, errors=None, warnings=None):

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

        if not isinstance(config, dict):
            return errors.error(ValidationError(path[-1], path, config, "dictionary expected"))

        for key, value in config.items():
            try:
                attribute = getattr(cls, key, None)
                if attribute is None:
                    raise ValidationWarning(key, path, value, "unknown attribute")
                else:
                    attribute.validate(value, path+[key], errors=errors, warnings=warnings)
            except ValidationError as error:
                errors.error(error)
            except ValidationWarning as warning:
                warnings.warning(warning)

        for name, attribute in cls.attributes():
            if name not in config and getattr(attribute, "default_handler", None) is None:
                errors.error(ValidationError(attribute, path+[name], None, "missing"))

        return config


def validate(schema, config, raise_errors=False, log=None):
    """
    Helper function that allows to validat a schema and either collect or raise
    errors

    Arguments:
        - schema <Schema>
        - config <dict|munge.Config>

    Keyword Arguments:
        - raise_errors <bool=False>: if True will raise a ValidationError exception
            if it encounters validation errors

            If False it will instead collect errors and warnings and return a tuple:

            success<bool>, errors<CollectValidationExceptions>, warnings<CollectValidationException>
    """

    if raise_errors:
        schema.validate(config)

    else:
        errors = CollectValidationExceptions()
        warnings = CollectValidationExceptions()
        schema.validate(config, errors=errors, warnings=warnings)

        success = len(errors) == 0

        if log and callable(log):
            for error in errors:
                log("[Config Error] {}".format(error.pretty))
            for warning in warnings:
                log("[Config Warning] {}".format(warning.pretty))
            if not success:
                log("{} errors, {} warnings in config".format(len(errors), len(warnings)))

        return (success, errors, warnings)
