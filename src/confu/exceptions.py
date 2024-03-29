from __future__ import annotations

from typing import Any

import confu.schema


class SoftDependencyError(ImportError):
    """
    Raised when a feature requires a dependency that is missing
    """

    def __init__(self, dep_name):
        super().__init__(f"To use this feature this dependency is required: {dep_name}")


class ValidationErrorBase(ValueError):
    """
    Config validation error interface
    """

    def __init__(
        self,
        attribute: confu.schema.Attribute,
        path: list[str],
        value: Any,
        reason: str,
    ) -> None:
        """
        **Arguments**

        - attribute (`Attribute`): confu attribute instance
        - path (`list`): attribute path
        - value (`mixed`): value that caused the validation error
        - reason (`str`): human readable reason message for validation error
        """

        msg = f"{path}: {reason}"
        self.details = {
            "path": path,
            "attribute": attribute,
            "value": value,
            "reason": reason,
        }
        super().__init__(msg)

    @property
    def pretty(self) -> str:
        """
        pretty formatted error message
        """
        return "{}: {}".format(
            ".".join([str(i) for i in self.details["path"]]), self.details["reason"]
        )

    def __eq__(self, other: ValidationError) -> bool:
        if type(other) != type(self):
            return False

        return (
            self.details["path"] == other.details["path"]
            and self.details["value"] == other.details["value"]
            and self.details["reason"] == other.details["reason"]
        )


class ValidationWarning(ValidationErrorBase):
    """
    Config validation warning
    """

    pass


class ValidationError(ValidationErrorBase):
    """
    Config validation error
    """

    pass


class ApplyDefaultError(ValidationErrorBase):
    """
    Raised when an exception occured during apply_defaults
    """

    def __str__(self) -> str:
        return self.pretty
