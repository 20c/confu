import json

import ipaddress

class JSONEncoder(json.JSONEncoder):

    """
    A very straight forward json encoder
    that will fallback to string formatted
    value on any object it can't serialize
    """

    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return "{}".format(obj)
