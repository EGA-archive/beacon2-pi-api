import beacon.conf.conf_default as _defaults
import datetime


class Config:
    pass


config = Config()

# Load defaults
for key in dir(_defaults):
    if key.isupper() or not key.startswith("_"):
        setattr(config, key, getattr(_defaults, key))

# Override with user config if present
try:
    import beacon.conf.conf as _userconf

    for key in dir(_userconf):
        if not key.startswith("_"):
            setattr(config, key, getattr(_userconf, key))
except ImportError as e:
    print('ERROR - {}Z - Failed to load: {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], e), flush=True)
    pass
