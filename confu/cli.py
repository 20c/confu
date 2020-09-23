"""
functions that allow you to generate CLI parameters from a confu schema for
argparse or click
"""

try:
    import click
except ImportError:
    pass


def option_name(path, delimiter="--"):
    """
    Returns a cli option name from attribute path

    **Arguments**

    - path (`list`): attribute path
    - delimiter (`str`): delimiter for nested attributes

    **Returns**

    cli option name (`str`)
    """

    return "--{}".format(delimiter.join(path).replace("_", "-"))


def destination_name(path, delimiter="__"):
    """
    Returns a cli option destination name from attribute path

    **Arguments**

    - path (`list`): attribute path
    - delimiter (`str`): delimiter for nested attributes

    **Returns**

    cli destination name (`str`)
    """
    return "{}".format(delimiter.join(path))


def default(value, path, defaults):
    if not defaults or not path:
        return value
    container = defaults
    for key in path:
        if key not in container:
            return value
        container = container[key]
    return container


def argparse_options(
    parser, schema, defaults=None, attributes=None, default_from_schema=True
):

    """
    Add cli options to an argparse ArgumentParser instance

    **Arguments**

    - parser (`argparse.ArgumentParser`)
    - schema (`Schema`)

    **Keyword Arguments**

    - defaults (`dict`): if specified will override defaults from here
    - attributes (`list<str>`): can hold a list of attribute names.
    if specified only matching attributes will be aded
    """

    def optionize(attribute, path):
        if not attribute.cli:
            return

        if attributes and destination_name(path) not in attributes:
            return

        kwargs = {
            "type": lambda x: attribute.validate(x, path),
            "help": attribute.help,
            "dest": destination_name(path),
        }

        if default_from_schema:
            kwargs["default"] = default(attribute.default, path, defaults)
        else:
            kwargs["default"] = default(None, path, defaults)

        name = option_name(path, delimiter=".")

        finalize = getattr(attribute, "finalize_argparse", None)
        if finalize:
            name = finalize(kwargs, name)

        if kwargs["default"] is not None and attribute.cli_show_default:
            kwargs["help"] = "{} ({})".format(kwargs["help"], kwargs["default"])

        parser.add_argument(name, **kwargs)

    schema.walk(optionize)


def apply_argparse(args, config):
    for k in args.__dict__:
        apply_arg(k, args, config)
    return config


def apply_arg(original_key, args, config):
    path = original_key.split("__")
    if len(path) > 1:
        data = config.data
        for key in path[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[path[-1]] = getattr(args, original_key)
    else:
        config.data[original_key] = getattr(args, original_key)


class click_options:

    """
    Add cli options to a click decorated function

    Use like a decorator

    **Arguments**

    - schema (`Schema`)

    **Keyword Arguments**

    - defaults (`dict`): if specified will override defaults from here
    - attributes (`list<str>`): can hold a list of attribute names.
    if specified only matching attributes will be aded
    """

    def __init__(self, schema, defaults=None, attributes=None):
        self.schema = schema
        self.defaults = defaults
        self.attributes = attributes

    def __call__(self, fn):
        container = {"fn": fn}
        defaults = self.defaults
        attributes = self.attributes

        def optionize(attribute, path):
            if not attribute.cli:
                return

            if attributes and destination_name(path) not in attributes:
                return

            def validate_and_convert(value):
                return attribute.validate(value, path)

            validate_and_convert.__name__ = attribute.__class__.__name__

            kwargs = {
                "type": click.types.FuncParamType(validate_and_convert),
                "help": attribute.help,
                "default": default(attribute.default, path, defaults),
            }

            name = option_name(path)

            finalize = getattr(attribute, "finalize_click", None)
            if finalize:
                name = finalize(kwargs, name)

            if kwargs["default"] is not None and attribute.cli_show_default:
                kwargs["help"] = "{} ({})".format(kwargs["help"], kwargs["default"])

            container["fn"] = click.option(
                name, destination_name(path), **kwargs
            ).__call__(fn)

        self.schema.walk(optionize)
        return container["fn"]
