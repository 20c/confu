You can use confu schemas to generate and validate command line options and arguments.

We currently support both `argparse` as well as `click` for this.

# Argparse integration

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

# Click integration

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


