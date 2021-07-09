# Install

Install using pip

```
pip install confu
```

# Defining a schema

```py
from confu import schema

class MySchema(schema.Schema):
    some_number = schema.Int(help="Some integer")
    some_string = schema.Str(default="something", help="An arbitrary string")
    some_list = schema.List(schema.Int(), help="A list of integers")
    some_bool = schema.Bool(default=False)

    class Sub(schema.Schema):
        nested_string = schema.Str(default="something nested", help="A nested string")
    sub = Sub()
```

# Validating a schema

Once the schema is defined you can validate a dict or munge.Config instance against it

```py
from confu.schema import validate

# prepare a config that will pass validation
config_passes = {
  "sub": {
    "nested_string": "what"
  },
  "some_number": 123,
  "some_string": "hello",
  "some_list": [
    123
  ]
}

# prepare a config that will fail validation
config_fails = {
  "some_number": "not a number"
}

# validate succesfully
# success = True
success, errors, warnings = validate(MySchema(), config_passes)

# fail to validate
# sucess = False
success, errors, warnings = validate(MySchema(), config_fails)
```

### Print errors on failed validation

```py
# fail to validate and print warnings
success, errors, warnings = validate(MySchema(), config_fails, log=print)
```

Will output

```py
[Config Error] some_number: integer expected
[Config Error] sub: missing
2 errors, 0 warnings in config
```
