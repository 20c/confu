class SoftDependencyError(ImportError):
    """
    Raised when a feature requires a dependency that is missing
    """

    def __init__(self, dep_name):
        super(SoftDependencyError, self).__init__(
            "To use this feature this dependency is required: {}".format(dep_name)
        )


class ValidationErrorBase(ValueError):
    """
    Config validation error interface
    """

    def __init__(self, attribute, path, value, reason):
        """
        **Arguments**

        - attribute (`Attribute`): confu attribute instance
        - path (`list`): attribute path
        - value (`mixed`): value that caused the validation error
        - reason (`str`): human readable reason message for validation error
        """

        msg = "{}: {}".format(path, reason)
        self.details = {
            "path": path,
            "attribute": attribute,
            "value": value,
            "reason": reason,
        }
        super(ValidationErrorBase, self).__init__(msg)

    @property
    def pretty(self):
        """
        pretty formatted error message
        """
        return "{}: {}".format(
            ".".join([str(i) for i in self.details["path"]]), self.details["reason"]
        )

    def __eq__(self, other):
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

    def __str__(self):
        return self.pretty
