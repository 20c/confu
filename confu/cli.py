import argparse
from confu.schema import validate, Schema

try:
    import click
except ImportError:
    pass


def option_name(path, delimiter="--"):
    """returns a cli option name from attribute path"""
    return "--{}".format(delimiter.join(path).replace("_","-"))


def destination_name(path, delimiter="__"):
    """returns a cli option destination name from attribute path"""
    return "{}".format(delimiter.join(path))


def argparse_options(parser, schema):
    def optionize(attribute, path):
        if not attribute.cli:
            return

        kwargs = {
            "type" : lambda x: attribute.validate(x, path),
            "help" : attribute.help,
            "dest" : destination_name(path),
            "default" : attribute.default
        }

        name = option_name(path, delimiter=".")

        finalize = getattr(attribute, "finalize_argparse", None)
        if finalize:
            name = finalize(kwargs, name)
        parser.add_argument(name, **kwargs)

    schema.walk(optionize)


class click_options(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, fn):
        container = {"fn":fn}
        def optionize(attribute, path):
            if not attribute.cli:
                return

            def validate_and_convert(value):
                return attribute.validate(value, path)
            validate_and_convert.__name__ = attribute.__class__.__name__

            kwargs = {
                "type" : click.types.FuncParamType(validate_and_convert),
                "help" : attribute.help,
                "default" : attribute.default
            }

            name = option_name(path)

            finalize = getattr(attribute, "finalize_click", None)
            if finalize:
                name = finalize(kwargs, name)

            container["fn"] = click.option(name, destination_name(path), **kwargs).__call__(fn)
        self.schema.walk(optionize)
        return container["fn"]

