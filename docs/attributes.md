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

### Schema
holds a collection of attributes - can nest additional schemas

**Special properties**

*item* - `Attribute` - default: `None`: attribute that describes items held by this schema
if the schema describes a dict with arbitrary keys.

!!! Tip "`item` property cannot be set on schemas with defined attributes"
    The `item` property is solely used to allow a schema to validate a dictonary
    that has arbitrary key names. As such trying to set the `item` property on a schema
    that has attributes defined within will raise a `ValueError`

### Str
validates a string value

### Int
validates an integer value

### Float
validates a float value

### List
validates a list

**Special Properties**

*item* - `Attribute` - default: `None`: attribute that describes items held by this list

```py
my_list = confu.schema.List(name="my_list", item=confu.schema.Str())
```

### File
validates a file path, will raise a ValidationError if the specified file does not exist

### Directory
validates a directory path, the default behaviour is to raide a ValidationError if the specified
directory does not exist

**Special Properties**

  - *create* - `bool` - default: `False`: if True will create the directory

### Email
validates an email address

### Url
validates a url

Special Properties:
  - *schemes* - `list` - default: `[]`: A list of supported schemes - an empty list will allow all schemes

### IpAddress
validates a v4 or v6 ip address

!!! Tip "ipaddress module required"
    To use this attribute please install the python ipaddress module

    `pip install ipaddress`

**Special Properties**

  - *protocol* - `int` - default: `None`: Specifies the protocol can be `4`, `6` or `None`. If `None` both 4 and 6 type addresses are allowed.
