import re

try:
    #py2
    from urlparse import urlparse
except ImportError:
    #py3
    from urllib.parse import urlparse

from confu.schema.core import Str, ValidationError


class Email(Str):

    def validate(self, value, path, **kwargs):
        value = super(Email, self).validate(value, path, **kwargs)

        # TODO: any reason to get more sophisticated than this?
        if not re.match("[^@\s]+@[^@\s]+", value):
            raise ValidationError(self, path, value, "email address expected")

        return value


class Url(Str):

    def __init__(self, name="", **kwargs):
        super(Url, self).__init__(name=name, **kwargs)
        self.schemes = kwargs.get("schemes", [])

    def validate(self, value, path, **kwargs):
        """
        Currently only validates by running urlparse against it
        and checking that a scheme and netloc is set - and if a list of allowed
        schemes is provide that the scheme is valid against that list

        TODO: may want something more sophisticated than that - could look
        at django's url validator
        """
        value = super(Url, self).validate(value, path, **kwargs)

        try:
            result = urlparse(value)
        except:
            raise ValidationError(self, path, value, "url expected")

        if not result.scheme:
            raise ValidationError(self, path, value, "no url scheme specified")

        if not result.netloc:
            raise ValidationError(self, path, value, "no url netloc specified")

        if self.schemes and result.scheme not in self.schemes:
            raise ValidationError(self, path, value, "invalid url scheme: {}".format(result.scheme))

        return value
