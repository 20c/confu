# Specifications

## Overview

Implementation of configuration schema in python. Something that can be used to validate configuration files as well as generate configuration files.

We have a form of this implemented in [vodka/config](https://github.com/20c/vodka/tree/master/vodka/config), should take all the schema definition code from there and re-use it here. 

## Feature requirements

- Use [munge](https://github.com/20c/munge) for config file loading and saving
- Work with munge.Config
- Generate config file with default values (python -> yaml)
- Generate schema from config file (yaml -> python)
- Validate a config file - think django field validation but for config variables.
- Work with click and argparse

## Schema requirements

### Required

- `type`: config variable type (for example `int` or `str` or `url`), custom types should be allowed. This will also be used as a validator when validating the config)
- `name`: config variable name (this could come from an attribute or could be the property name in the schema)

### Optional

- `default`: default value to use if variable is missing from config file
- `help`: arbitrary help text describing the config variable and how to use it
- `deprecated_in`: version this config variable will be deprecated
- `added_in` : version this config variable was added
- `removed_in` : version this config variable was remove
- `choices` : array of possible value choices

Most yaml configurations will come with some sort of nesting. So need to be able to handle that, whether it's via lists or object literals or a combination.

#### Type

Describes the config variable type - this should be a function that can be used to validate the value. So for example
could be the `int` function that comes with python or a custom function that can take a value and then validate it 

## Validation

When validating a config file list error messages for all validation errors. The vodka implementation has errors and warnings, might make sense to have this separation here as well. Warnings could be used for exmaple to alert the user when they have config variables in their config file that the schema knows nothing about.

## Config file generation

Should be able to generate both ways.

### Python -> yaml

Generate a yaml file with default values from the schema

### Yaml -> Python

Generate a confu schema from a yaml file (name, type (str/int/float?) and possibly help from inline comments?)

## CLI

Should work with `click` and `argparse` to generate and validate files.
