"""
config management
"""


import collections
import copy

import confu.schema
from typing import Any
from typing import Dict
from typing import Optional


class Config(collections.abc.Mapping):
    """
    class for storing and manipulating config data
    """

    def __init__(self, schema: Any, data: Optional[Dict[str, Any]] = None, meta: Optional[Any] = None) -> None:
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

    def copy(self) -> Dict[str, Any]:
        """return a read only copy of data"""
        return copy.deepcopy(self.data)

    @property
    def data(self) -> Dict[str, Any]:
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
    def data(self, value: Dict[str, Any]) -> None:
        self._base_data = value
        self._data = None

    @property
    def schema(self) -> Any:
        """return a read only copy of schema"""
        return copy.deepcopy(self._schema)

    def get_nested(self, *args: str) -> Optional[Dict[str, int]]:
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

    def __iter__(self) -> dict_keyiterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)
