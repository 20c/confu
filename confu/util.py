"""
utility functions / classes
"""
import os

def config_parser_dict(config):
    """
    Takes a configparser.ConfigParser instance and returns a dict
    of sections and their keys and values

    **Arguments**

    - config (`configparser.ConfigParsers`)

    **Returns**

    dict
    """
    return {s: dict(config.items(s)) for s in config.sections()}


_DEFAULT_ARG = object()


def set_from_env(name, default=_DEFAULT_ARG):
    return _set_from_env(name, globals(), default)


def _set_from_env(name, context, default):
    """
    Sets a global variable from a environment variable of the same name.

    This is useful to leave the option unset and use Django's default
    (which may change).
    """
    if default is _DEFAULT_ARG and name not in os.environ:
        return

    context[name] = os.environ.get(name, default)


def set_option(name, value, envvar_type=None):
    return _set_option(name, value, globals(), envvar_type)


def _set_option(name, value, context, envvar_type=None):
    """
    Sets an option, first checking for env vars,
    then checking for value already set,
    then going to the default value if passed.
    Environment variables are always strings, but
    we try to coerce them to the correct type first by checking
    the type of the default value provided. If the default
    value is None, then we check the optional envvar_type arg.
    """

    # If value is in True or False we
    # call set_bool to take advantage of
    # its type checking for environment variables
    if isinstance(value, bool):
        return _set_bool(name, value, context)

    if value is not None:
        envvar_type = type(value)
    else:
        # If value is None, we'll use the provided envvar_type, if it is not None
        if envvar_type is None:
            raise ValueError(
                f"If no default value is provided for the setting {name} the envvar_type argument must be set."
            )

    if name in os.environ:
        env_var = os.environ.get(name)
        # Coerce type based on provided value
        context[name] = envvar_type(env_var)
    # If the environment variable isn't set
    else:
        _set_default(name, value, context)


def set_bool(name, value):
    return _set_bool(name, value, globals())


def _set_bool(name, value, context):
    """ Sets and option, first checking for env vars, then checking for value already set, then going to the default value if passed. """
    if name in os.environ:
        envval = os.environ.get(name).lower()
        if envval in ["1", "true", "y", "yes"]:
            context[name] = True
        elif envval in ["0", "false", "n", "no"]:
            context[name] = False
        else:
            raise ValueError(
                "{} is a boolean, cannot match '{}'".format(name, os.environ[name])
            )

    _set_default(name, value, context)


def set_default(name, value):
    return _set_default(name, value, globals())


def _set_default(name, value, context):
    """ Sets the default value for the option if it's not already set. """
    if name not in context:
        context[name] = value
