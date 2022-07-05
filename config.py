import json


class Config:
    WiiUCommonKey = None
    RhythmHeavenFeverTitleKey = None


with open("config.json", "r") as f:
    d = json.load(f)
    for k in d:
        setattr(Config, k, d[k])
