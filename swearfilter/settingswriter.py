# coding: utf-8


try:
    import ujson as json
except ModuleNotFoundError:
    import json


class Config:
    def __init__(self, fn):
        self.fn = fn

    def get(self):
        return json.loads(open(self.fn, encoding='utf-8').read())

    def set(self, new):
        with open(self.fn, 'w', encoding='utf-8') as f:
            f.write(json.dumps(new, ensure_ascii=False, sort_keys=True, indent=4))
