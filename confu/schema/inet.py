"""
Attributes that deal with networking specific values such as emails, urls and ip addresses

These can be imported directly from `confu.schema`

## Requirements

- `ipaddress` for ip address validation
"""

import re

try:
    # py2
    from urlparse import urlparse
except ImportError:
    # py3
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

    """
    Describes an email address
    """

    def validate(self, value, path, **kwargs):
        value = super(Email, self).validate(value, path, **kwargs)

        if value == "" and self.blank:
            return value

        if value is None and self.default_is_none:
            return value

        # TODO: any reason to get more sophisticated than this?
        if not re.match(r"[^@\s]+@[^@\s]+", value):
            raise ValidationError(self, path, value, "email address expected")

        return value


class Url(Str):

    """
    Describes a URL
    """

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

        if value == "" and self.blank:
            return value

        if value is None and self.default_is_none:
            return value

        try:
            result = urlparse(value)
        except:
            raise ValidationError(self, path, value, "url expected")

        if not result.scheme:
            raise ValidationError(self, path, value, "no url scheme specified")

        if not result.netloc:
            raise ValidationError(self, path, value, "no url netloc specified")

        if self.schemes and result.scheme not in self.schemes:
            raise ValidationError(
                self, path, value, "invalid url scheme: {}".format(result.scheme)
            )

        return value


class IpAddress(Str):

    """
    Describes a IPv4 or IPv6 address
    """

    def __init__(self, name="", protocol=None, **kwargs):

        """
        Initialize attribute

        **Keyword Arguments**

        - name (`str`): describes the attribute name, if not specified
          explicitly will be set through the schema that instantiates
          the attribute.
        - protocol (`int`): ip version, can be 4, 6 or None - if it is none
          the attribute can hold either a v4 or a v6 IP address.
        - default (`mixed`): the default value of this attribute. Once a default
          value is set, schema validation will no longer raise a
          validation error if the attribute is missing from the
          configuration.
        - choices (`list`): if specified on values in this list may be set
          for this attribute
        - help (`str`): help description
        - cli (`bool=True`): enable CLI support for this attribute
        - deprecated (`str`): version id of when this attribute will be deprecated
        - added (`str`): version id of when this attribute was added to the schema
        - removed (`str`): version id of when this attribute will be removed
        """

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

        if value is None and self.default_is_none:
            return value

        if self.blank and value == "":
            return value

        value = u"{}".format(value)
        value_v4 = self.validate_v4(value, path, **kwargs)
        value_v6 = self.validate_v6(value, path, **kwargs)
        if self.protocol == 4 and not value_v4:
            raise ValidationError(self, path, value, "invalid ip (v4)")
        elif self.protocol == 6 and not value_v6:
            raise ValidationError(self, path, value, "invalid ip (v6)")
        elif self.protocol is None and not value_v4 and not value_v6:
            raise ValidationError(self, path, value, "invalid ip (v4 or v6)")
        return value_v4 or value_v6
