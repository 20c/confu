import re

try:
    #py2
    from urlparse import urlparse
except ImportError:
    #py3
    from urllib.parse import urlparse

try:
    # we try to import the `ipaddress` module, which will be used
    # to validate ipaddress and prefix fields. However this should
    # be a soft requirement.
    import ipaddress
except ImportError:
    ipaddress = None

from confu.schema.core import Str, ValidationError
from confu.exceptions import SoftDependencyError


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


class IpAddress(Str):

    def __init__(self, name="", protocol=None, **kwargs):
        super(IpAddress, self).__init__(name=name, **kwargs)
        if not ipaddress:
            raise SoftDependencyError("ipaddress")
        if protocol not in [None, 4, 6]:
            raise ValueError("IpAddress protocol needs to be either 4, 6 or None")
        self.protocol = protocol

    def validate_v4(self, value, path, **kwargs):
        try:
            return ipaddress.IPv4Address(value)
        except ipaddress.AddressValueError:
            return False

    def validate_v6(self, value, path, **kwargs):
        try:
            return ipaddress.IPv6Address(value)
        except ipaddress.AddressValueError:
            return False

    def validate(self, value, path, **kwargs):
        value = super(IpAddress, self).validate(value, path, **kwargs)
        value = u"{}".format(value)
        value_v4 = self.validate_v4(value, path, **kwargs)
        value_v6 = self.validate_v6(value, path, **kwargs)
        if self.protocol == 4 and not value_v4:
            raise ValidationError(self, path, value, "invalid ip (v4)")
        elif self.protocol == 6 and not value_v6:
            raise ValidationError(self, path, value, "invalid ip (v6)")
        elif self.protocol is None and not value_v4 and not value_v6:
            raise ValidationError(self, path, value, "invalid ip (v4 or v6)")
        return (value_v4 or value_v6)
