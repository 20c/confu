"""
config management
"""

from __future__ import annotations

import collections
import copy
from typing import Any, Iterator

import confu.schema


class Config(collections.abc.Mapping):
    """
    class for storing and manipulating config data
    """

    def __init__(
        self,
        schema: confu.schema.Schema,
        data: dict | None = None,
        meta: dict | None = None,
    ) -> None:
        """
        **Arguments**

        - schema (`confu.schema`): schema object

        **Keyword Arguments**

        - data (`dict`): dict to set initial data
        - meta (`dict`): any additional metadata to pass along with config
        """
        self._base_data = None
        self._data = None
        self._schema = schema
        self.meta = meta if meta else {}

        self.errors = []
        self.warnings = []
        self.valid = None

        # use property setter to apply
        self.data = data if data else {}

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self.data == other.data

    def copy(self) -> dict:
        """return a read only copy of data"""
        return copy.deepcopy(self.data)

    @property
    def data(self) -> dict:
        """config data, should be used for read only"""
        if self._data:
            return self._data

        data = copy.deepcopy(self._base_data)

        try:
            confu.schema.apply_defaults(self._schema, data)
        except confu.exceptions.ApplyDefaultError as exc:
            self.apply_default_error = exc

        self.valid, self.errors, self.warnings = confu.schema.validate(
            self.schema, data
        )

        if hasattr(self, "apply_default_error"):
            self.errors.exceptions.insert(0, self.apply_default_error)

        self._data = data
        return self._data

    @data.setter
    def data(self, value: dict) -> None:
        self._base_data = value
        self._data = None

    @property
    def schema(self) -> confu.schema.Schema:
        """return a read only copy of schema"""
        return copy.deepcopy(self._schema)

    def get_nested(self, *args: str) -> dict | None:
        """
        get a nested value, returns None if path does not exist
        """
        data = self.data
        for key in args:
            if key not in data:
                return None
            data = data[key]
        return data

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __iter__(self) -> Iterator[dict.keys]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)
