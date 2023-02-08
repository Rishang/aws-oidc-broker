import os
import json
import dataclasses
from typing import Dict


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def FilterDataclass(data: dict, obj):
    """"""

    out: dict = dict()
    names = set([f.name for f in dataclasses.fields(obj)])
    for k, v in data.items():
        if k in names:
            out[k] = v
    return obj(**out)


class State:
    def __init__(self, file_path: str, obj):
        self.state: dict = {}
        self.cache: object
        self.state_file = file_path
        self.obj = obj
        self.load()

    def load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                _s = json.load(f)
                if len(_s) == 0:
                    return
                for k in _s:
                    if dataclasses.is_dataclass(self.obj):
                        self.state[k] = FilterDataclass(_s[k], obj=self.obj)

    def save(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, cls=EnhancedJSONEncoder)

    def get(self, key: str) -> Dict:
        return self.state.get(key)  # type: ignore

    def set(self, key: str, value):
        self.state[key] = value

    def items(self):
        return self.state.items()

    def keys(self):
        return self.state.keys()

    def pop(self, key: str):
        self.state.pop(key)

    def __getitem__(self, key: str) -> Dict:
        return self.state[key]

    def __setitem__(self, key: str, value: Dict):
        self.state[key] = value
        self.save()

    def __delitem__(self, key: str):
        del self.state[key]
        self.save()

    def __contains__(self, key: str) -> bool:
        return key in self.state

    def __len__(self) -> int:
        return len(self.state)

    def __repr__(self) -> str:
        return repr(self.state)

    def __eq__(self, other: object) -> bool:
        return self.state == other

    def __ne__(self, other: object) -> bool:
        return self.state != other
