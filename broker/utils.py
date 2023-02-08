import os
from dotenv import dotenv_values


class Message:
    """Send dict message responses for json response"""

    def __init__(self) -> None:
        pass

    def info(self, message: str):
        return {"INFO": message}

    def sucess(self, message: str):
        return {"SUCESS": message}

    def error(self, message: str):
        return {"ERROR": message}


msg = Message()


def obj_annotations(obj: object):
    return [i[0] for i in obj.__annotations__.items()]


def load_or_read_env(items: list[str], env_path: str):
    conf = {}

    if os.path.isfile(env_path):
        conf = dotenv_values(env_path)
    for i in items:
        if os.environ.get(i):
            conf[i] = os.environ.get(i)

    return conf
