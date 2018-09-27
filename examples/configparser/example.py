try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from confu.schema import (IpAddress, Int, Schema, validate)

# this schema describes the [server] section
class ServerSchema(Schema):
    host = IpAddress("host")
    port = Int("port", default=80)

# this schema describes the entire config
class ConfigSchema(Schema):
    # server schema as sub schema
    server = ServerSchema()

# read config
config = configparser.ConfigParser()
config.read("config.cfg")

# validate config
success, errors, warnings = validate(ConfigSchema(), config, log=print)
