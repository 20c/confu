"""
utility functions / classes
"""
import os


def config_parser_dict(config):
    """
    Takes a configparser.ConfigParser instance and returns a dict
    of sections and their keys and values.

    **Arguments**

    - config (`configparser.ConfigParsers`)

    **Returns**

    dict
    """
    return {s: dict(config.items(s)) for s in config.sections()}


_DEFAULT_ARG = object()


class SettingsManager:
    """
    Scoped settings management with environment variable override support.
    """

    def __init__(self, scope, name="settings_manager"):
        """
        **Arguments**

        - scope (`dict`)

        **Keyword Arguments**

        - name (`str`): name of the variable used for the object instance, default = "settings_manager"
        """

        self.scope = scope
        self.name = name

    def set_from_env(self, name, default=_DEFAULT_ARG):
        """
        Sets a scope variable from a environment variable of the same name.

        It is useful to leave the option unset and use default if it
        already exists in the scope.

        **Arguments**

        - name (`str`)

        **Keyword Arguments**

        - default: value to be used incase there is no environment variable
        """
        if default is _DEFAULT_ARG and name not in os.environ:
            return

        self.scope[name] = os.environ.get(name, default)

    def set_option(self, name, value, envvar_type=None):
        """
        Sets an option, first checking for environment variables,
        then checking for value already set,
        then going to the value passed.
        Environment variables are always strings, but
        we try to coerce them to the correct type first by checking
        the type of the default value provided. If the default
        value is None, then we check the optional envvar_type arg.

        **Arguments**

        - name (`str`): name of variable, default = "settings_manager"
        - value : If None is passed a envar_type needs to be given

        **Keyword Arguments**

        - envar_type
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
        """
        Sets an option, first checking for environment variables,
        then checking for value already set,
        then going to the value passed.
        Environment variable values of "1", "true", "y" or "yes" (can be in any case) are considered `True`.
        Environment variable values of "0", "false", "n" or "no" (can be in any case) are considered `False`.

        **Arguments**

        - name (`str`)
        - value
        """
        if name in os.environ:
            envval = os.environ.get(name).lower()
            if envval in ["1", "true", "y", "yes"]:
                self.scope[name] = True
            elif envval in ["0", "false", "n", "no"]:
                self.scope[name] = False
            else:
                raise ValueError(
                    f"{name} is a boolean, cannot match '{os.environ[name]}'"
                )
        self.set_default(name, value)

    def set_default(self, name, value):
        """
        Sets the default value for the option if a value is not already set.

        **Arguments**

        - name (`str`)
        - value
        """
        if name not in self.scope:
            self.scope[name] = value

    def try_include(self, filepath):
        """
        Tries to include another file into current scope.

        **Arguments**

        - filepath (`str`): path to the file trying to be included.
        """
        try:
            with open(filepath) as f:
                self.scope[self.name] = self
                exec(compile(f.read(), filepath, "exec"), self.scope)

        except FileNotFoundError:
            pass
