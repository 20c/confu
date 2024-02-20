"""
utility functions / classes
"""
from __future__ import annotations

import os
from configparser import ConfigParser
from typing import Any

from confu.types import TimeDuration


def config_parser_dict(config: ConfigParser) -> dict:
    """
    Takes a configparser.ConfigParser instance and returns a dict
    of sections with their keys and values.

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

    def __init__(self, scope: dict[str, Any], name: str = "settings_manager") -> None:
        """
        **Arguments**

        - scope (`dict`)

        **Keyword Arguments**

        - name (`str`): name of the variable used for the object instance, default = "settings_manager"
        """

        self.scope = scope
        self.name = name

    def set_from_env(self, name: str, default: object | str = _DEFAULT_ARG) -> None:
        """
        Sets a scope variable from an environment variable of the same name.

        It is useful to leave the option unset and use default if it
        already exists in the scope.

        **Arguments**

        - name (`str`)

        **Keyword Arguments**

        - default: value to be used if there is no environment variable
        of the same name
        """
        if default is _DEFAULT_ARG and name not in os.environ:
            return

        self.scope[name] = os.environ.get(name, default)

    def set_option(
        self, name: str, value: Any, envvar_type: type | None = None
    ) -> Any | None:
        """
        Sets an option by first checking for environment variables,
        then checking for value already set,
        then going to the `value` argument passed.
        Environment variables are always strings that are
        first coerced to the correct type by checking
        the type of the `value` argument. If the value
        passed is `None`, then the optional envvar_type argument
        is checked (If you want to set the option to `None`,
        pass the envvar_type as `type(None)`).

        **Arguments**

        - name (`str`): name of variable, default = "settings_manager"
        - value: If `None` is passed a envar_type needs to be given

        **Keyword Arguments**

        - envvar_type
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

    def set_list(
        self,
        name: str,
        value: list[str],
        envvar_element_type: type | None = None,
        delimiter: str = ",",
    ) -> None:
        """
        Sets an option to be a list by first checking for environment variables,
        then checking for value already set,
        then going to the `value` argument passed.
        Environment variable values are split by commas.

        Supports only single level single type lists.

        The `value` arguments's first element's type is used to coerce the environment variable's
        value to the correct type.
        If the value passed is `None`, or an empty list, then the optional element_type argument
        is used to coerce the list elements to the correct type.

        **Arguments**

        - name (`str`)
        - value

        **Keyword Arguments**

        - envvar_element_type
        - delimiter
        """
        if value is not None and len(value) > 0:
            envvar_element_type = type(value[0])
        else:
            # If value is None or value array is empty, we'll use the provided envvar_type, if it is not None
            if envvar_element_type is None:
                raise ValueError(
                    f"If no default value is provided for the setting {name} the envvar_element_type argument must be set."
                )

        if name in os.environ:
            array = os.environ.get(name).split(delimiter)
            # coerce elements to the correct type
            self.scope[name] = [envvar_element_type(element) for element in array]
        else:
            self.set_default(name, value)

    def set_bool(self, name: str, value: bool) -> None:
        """
        Sets an option by first checking for environment variables,
        then checking for value already set,
        then going to the `value` argument passed.
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

    def set_default(self, name: str, value: bool | TimeDuration | str) -> None:
        """
        Sets the default value for the option if a value is not already set.

        **Arguments**

        - name (`str`)
        - value
        """
        if name not in self.scope:
            self.scope[name] = value

    def try_include(self, filepath: str) -> None:
        """
        Tries to include another file into the current scope.

        **Arguments**

        - filepath (`str`): path to the file trying to be included.
        """
        try:
            with open(filepath) as f:
                self.scope[self.name] = self
                exec(compile(f.read(), filepath, "exec"), self.scope)

        except FileNotFoundError:
            pass
