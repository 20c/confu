# Confu

[![PyPI](https://img.shields.io/pypi/v/cfu.svg?maxAge=60)](https://pypi.python.org/pypi/cfu)
[![PyPI](https://img.shields.io/pypi/pyversions/cfu.svg?maxAge=600)](https://pypi.python.org/pypi/cfu)
[![Travis CI](https://img.shields.io/travis/20c/confu.svg?maxAge=60)](https://travis-ci.org/20c/confu)
[![Codecov](https://img.shields.io/codecov/c/github/20c/confu/master.svg?maxAge=60)](https://codecov.io/github/20c/confu)

Configuration validation and generation

Supports:
  - python 2.7
  - python 3.4
  - python 3.5
  - python 3.6

# Install

Install using pip

```
pip install cfu
```

# Quickstart

## Defining a schema

```py
from confu import schema

class MySchema(schema.Schema):
    some_number = schema.IntAttribute("some_number", help="Some integer")
    some_string = schema.StringAttribute("some_string", default="something", help="An arbitrary string")
    some_list = schema.ListAttribute("some_list", schema.IntAttribute("some_list.item"), help="A list of integers")
    some_bool = schema.BoolAttribute("some_bool", default=False)

    class sub(schema.Schema):
        nested_string = schema.StringAttribute("nested_string", default="something nested", help="A nested string")
```

## Validating a schema

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
success, errors, warnings = validate(MySchema, config_passes)

# fail to validate
# sucess = False
success, errors, warnings = validate(MySchema, config_fails)
```

### Print errors on failed validation

```py
# fail to validate and print warnings
success, errors, warnings = validate(MySchema, config_fails, log=print)
```

Will output

```py
[Config Error] some_number: integer expected
[Config Error] sub: missing
2 errors, 0 warnings in config
```

## Click and config file validation

In this example we load a yaml config file using munge and validate it against our schema.

We use click as an arg parser.

```py
import click
from confu.schema import validate
from myschema import MySchema
from munge.config import Config


@click.command()
@click.option('--config', envvar='APPNAME_HOME', default=click.get_app_dir('appname'))
def do_stuff(config):
    cfg = Config(read=config)
    success, errors, warnings = validate(MySchema, cfg, log=click.echo)
    if not success:
        raise click.ClickException("Configuration invalid")

if __name__ == "__main__":
    do_stuff()
```

## Argparse and config file validation

In this example we load a yaml config file using munge and validate it against our schema.

We use python argparse as an arg parser.

```py
import sys
import argparse
from confu.schema import validate
from myschema import MySchema
from munge.config import Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    args = parser.parse_args()

    cfg = Config(read=args.config)
    success, errors, warnings = validate(MySchema, cfg, log=print)
    if not success:
        sys.exit(1)
```

## Click options from schema

It is also possible to generate click options using your confu schema

```py
import click
from confu.schema import validate
from confu.cli import click_options
from myschema import MySchema


@click.command()
@click_options(MySchema)
def do_stuff(**kwargs):
    print(kwargs)
if __name__ == "__main__":
    do_stuff()
```

Passing --help to test

```
python do_stuff.py --help
Usage: do_stuff.py [OPTIONS]

Options:
  --sub--nested-string STRINGATTRIBUTE
                                  A nested string
  --some-string STRINGATTRIBUTE  An arbitrary string
  --some-number INTATTRIBUTE      Some integer
  --some-list LISTATTRIBUTE       A list of integers
  --some-bool / --no-some-bool
  --help                          Show this message and exit.
```

## Argparse options from schema

It is also possible to generate argparse arguments using your confu schema

```py
import argparse
from confu.cli import argparse_options
from myschema import MySchema
from munge.config import Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argparse_options(parser, MySchema)
    parser.parse_args()
```

Passing --help to test

```
python do_stuff.py --help
usage: do_stuff.py [-h] [--some-bool] [--some-list SOME_LIST]
                                   [--some-number SOME_NUMBER]
                                   [--some-string SOME_STRING]
                                   [--sub.nested-string SUB__NESTED_STRING]

optional arguments:
  -h, --help            show this help message and exit
  --some-bool
  --some-list SOME_LIST
                        A list of integers
  --some-number SOME_NUMBER
                        Some integer
  --some-string SOME_STRING
                        An arbitrary string
  --sub.nested-string SUB__NESTED_STRING
                        A nested string
```
