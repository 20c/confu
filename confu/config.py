from __future__ import (absolute_import, division, print_function)

import collections
import copy

import confu.schema


class Config(collections.Mapping):
    """
    class for storing and manipulating config data
    """

    def __init__(self, schema, data=None, meta=None):
        """
        `schema` confu.schema object
        `data` dict to set initial data
        `meta` any addition metadata to pass along with config
        """
        self._base_data = None
        self._data = None
        self._schema = schema
        self.meta = meta if meta else {}

        self.errors = []
        self.warnings = []

        # use property setter to apply
        self.data = data if data else {}

    def copy(self):
        """ return a read only copy of data """
        return copy.deepcopy(self.data)

    @property
    def data(self):
        """ config data, should be used for read only """
        if self._data:
            return self._data

        data = copy.deepcopy(self._base_data)
        confu.schema.apply_defaults(self._schema, data)
        valid, self.errors, self.warnings = confu.schema.validate(self.schema, data)
        self._data = data
        return self._data

    @data.setter
    def data(self, value):
        self._base_data = value
        self._data = None

    @property
    def schema(self):
        """ return a read only copy of schema """
        return copy.deepcopy(self._schema)

    def get_nested(self, *args):
        """
        get a nested value, returns None if path does not exist
        """
        data = self.data
        for key in args:
            if key not in data:
                return None
            data = data[key]
        return data

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
