class ValidationErrorBase(ValueError):
    def __init__(self, attribute, path, value, reason):
        msg = "{}: {}".format(path, reason)
        self.details = {
            "path" : path,
            "attribute" : attribute,
            "value" : value,
            "reason" : reason
        }
        super(ValidationErrorBase, self).__init__(msg)

    @property
    def pretty(self):
        return "{}: {}".format(".".join(self.details["path"]), self.details["reason"])

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return (self.details["path"] == other.details["path"] and
                self.details["value"] == other.details["value"] and
                self.details["reason"] == other.details["reason"])



class ValidationWarning(ValidationErrorBase):
    pass

class ValidationError(ValidationErrorBase):
    pass


