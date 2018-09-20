import re

from confu.schema.core import Str, ValidationError

class Email(Str):

    def validate(self, value, path, **kwargs):
        value = super(Email, self).validate(value, path, **kwargs)

        if not re.match("[^@\s]+@[^@\s]+", value):
            raise ValidationError(self, path, value, "email address expected")

        return value
