import json


class _ConfigType(type):
    def __getattr__(cls, key):
        if getattr(cls, key, None) is None:
            with open("config.json", "r") as f:
                cls.__dict__.update(json.load(f))

        if key in cls.__dict__:
            return cls.__dict__[key]
        raise AttributeError(key)


class Config:
    __metaclass__ = _ConfigType
    WiiUCommonKey = None
    RhythmHeavenFeverTitleKey = None
