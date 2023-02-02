import hashlib
import pathlib

import typer
from rich import print as pprint
from rich.prompt import Prompt

HOME = f"{pathlib.Path.home()}"
prompt = Prompt()


class Logger:
    def error(self, message, exit: bool = False):
        pprint(f"\n[red]ERROR: {message}")
        if exit:
            raise typer.Exit(code=1)

    def info(self, message):
        pprint(f"\n[red]INFO: {message}")


log = Logger()


def md5hash(value: str):
    result = hashlib.md5(value.encode())
    return result.hexdigest()


def isNone(val):
    if val == None:
        return True
    elif isinstance(val, str) and val != "":
        return False
    elif isinstance(val, dict) and val != {}:
        return False
    elif isinstance(val, list) and val != []:
        return False
    return True
