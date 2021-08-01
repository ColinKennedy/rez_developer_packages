name = "rez_bisect"

version = "1.0.0"

description = "Like 'git bisect', but for Rez. Find which packages / versions introduced some issue."

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = ["python-2.7+<4"]

build_command = "python -m rez_build_helper --items bin python"

_test_requires = ["rez-2.93+<3"]

tests = {
    "black_diff": {
        "command": "black --diff --check package.py python tests",
        "requires": ["black-19"],
    },
    "black": {
        "command": "black package.py python tests",
        "requires": ["black-19"],
        "run_on": "explicit",
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": _test_requires + ["python-2"],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": _test_requires + ["python-3"],
    },
}

def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
