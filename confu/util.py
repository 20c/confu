"""
utility functions / classes
"""


def config_parser_dict(config):
    """
    Takes a configparser.ConfigParser instance and returns a dict
    of sections and their keys and values

    **Arguments**

    - config (`configparser.ConfigParsers`)

    **Returns**

    dict
    """
    return {s: dict(config.items(s)) for s in config.sections()}
