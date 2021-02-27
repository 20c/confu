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


class SettingsManager:

    """
    Scoped settings management with environment variable override support
    """

    def __init__(self, scope):

        """
        Arguments:

        - scope (`dict`)
        """

        self.scope = scope

    def set_from_env(self, name, default=_DEFAULT_ARG):
        """
        Sets a scope variable from a environment variable of the same name.

        This is useful to leave the option unset and use default if it
        already exists in the scope (which may change).
        """
        if default is _DEFAULT_ARG and name not in os.environ:
            return

        self.scope[name] = os.environ.get(name, default)

    def set_option(self, name, value, envvar_type=None):
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
            return self.set_bool(name, value)

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
            self.scope[name] = envvar_type(env_var)
        # If the environment variable isn't set
        else:
            self.set_default(name, value)

    def set_bool(self, name, value):
        """ Sets and option, first checking for env vars, then checking for value already set, then going to the default value if passed. """
        if name in os.environ:
            envval = os.environ.get(name).lower()
            if envval in ["1", "true", "y", "yes"]:
                self.scope[name] = True
            elif envval in ["0", "false", "n", "no"]:
                self.scope[name] = False
            else:
                raise ValueError(
                    "{} is a boolean, cannot match '{}'".format(name, os.environ[name])
                )
        self.set_default(name, value)

    def set_default(self, name, value):
        """ Sets the default value for the option if it's not already set. """
        if name not in self.scope:
            self.scope[name] = value
