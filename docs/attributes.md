All schema attributes can be imported from the `confu.schema` namespace

```py
from confu.schema import Str
```

# Attribute properties

All attributes have these possible properties

**name** - `str` - default: `""`
Used to identify the attribute during validation, mandatory on first level attributes, can be omitted on attributes that are describing list items.

**default** - `mixed` - default: `None`
The default value that will be used if no value is set for the attribute. This itself defaults to
None and in that case the attribute will be seen as mandatory and raise a validation error
if not set.

**help** - `str` - default: `None`
Help text - should describe what the attribute is for

**added** - `str|int|tuple` - default: `None`
Version in which this attribute was added

**deprecated** - `str|int|tuple` - default: `None`
Version in which this attribute will be deprecated

**removed** - `str|int|tuple` - default: `None`
Version in which this attributed will be removed

**cli** - `bool` - default: `True`
Enable this attribute when working with a CLI interface

# Attribute Types

Confu comes with several commonly used attributes out of the box.

They can all be imported from `confu.schema`

**confu.schema.Schema** - a collection of attributes - can nest additional schemas

**confu.schema.Str** - a string value

**confu.schema.Int** - an integer value

**confu.schema.Float** - a float value

**confu.schema.List** - a list

Special Properties:
  - *item* - `Attribute` - default: `None`: attribute that describes items held by this list

```py
my_list = confu.schema.List(name="my_list", item=confu.schema.Str())
```

**confu.schema.File** - a filepath
**confu.schema.Directory** a directory path

Special Properties:
  - *create* - `bool` - default: `False`: if True will create the directory

**confu.schema.Email** - an email address
**confu.schema.Url** - a url

Special Properties:
  - *schemes* - `list` - default: `[]`: A list of supported schemes - an empty list will allow all schemes

**confu.schema.IpAddress** - an ip address

Special Properties:
  - *protocol* - `int` - default: `None`: Specifies the protocol can be `4`, `6` or `None`. If `None` both 4 and 6 type addresses are allowed.
