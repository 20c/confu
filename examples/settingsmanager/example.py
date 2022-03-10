import os

from confu.util import SettingsManager, config_parser_dict



# using local scope g
g = {}
settings_manager = SettingsManager(g)
settings_manager.set_option("TEST_SETTING", "world")
print(g["TEST_SETTING"])

# using Global scope
settings_manager = SettingsManager(globals())
settings_manager.set_option("TEST_SETTING", "world")
print(TEST_SETTING)

# setting from env
os.environ["ENV_SETTING"] = "my_setting" #setting env variable
settings_manager.set_from_env("ENV_SETTING")
print(ENV_SETTING)

# setting boolean 
settings_manager.set_bool("BOOL_SETTING", False)
print(BOOL_SETTING)

# setting boolean overriden from env var from env
os.environ["ENV_BOOL"] = "True" #setting env variable
settings_manager.set_bool("ENV_BOOL", False)
print(ENV_BOOL)

# setting int from env
os.environ["ENV_INT"] = "123" #setting env variable
settings_manager.set_option("ENV_INT", None, envvar_type=int)
print(ENV_INT)

# setting default
settings_manager.set_default("DEFAULT_SETTING", 'my_defualt')
print(DEFAULT_SETTING)

# include another file (./test.py)
settings_manager.try_include('./test.py')
print(EXTERNAL_SETTING)