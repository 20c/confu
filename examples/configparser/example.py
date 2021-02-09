import configparser

from confu.schema import Int, IpAddress, Schema, validate


# this schema describes the [server] section
class ServerSchema(Schema):
    host = IpAddress()
    port = Int(default=80)


# this schema describes the entire config
class ConfigSchema(Schema):
    # server schema as sub schema
    server = ServerSchema()


# read config
config = configparser.ConfigParser()
config.read("config.cfg")

# validate config
success, errors, warnings = validate(ConfigSchema(), config, log=print)
