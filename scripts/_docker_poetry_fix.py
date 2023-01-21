import os
import tomli

WORKDIR = "."


def py_fix(path: str, mkdir: bool = True, file: str = ""):
    if mkdir:
        if not os.path.exists(path):
            os.mkdir(path)
            with open(os.path.join(path, "__init__.py"), "w") as fp:
                pass
    elif not mkdir:
        file_path=os.path.join(path, file)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                pass


with open(f"{WORKDIR}/pyproject.toml") as f:
    pyproject = tomli.loads(f.read())
    packages = pyproject["tool"]["poetry"]["packages"]
    readme = pyproject["tool"]["poetry"]["readme"]


if os.environ.get("PYTHONDONTWRITEBYTECODE"):
    for package in packages:
        py_fix(f"{WORKDIR}/{package['include']}")

    py_fix(path=WORKDIR, mkdir=False, file=readme)
