name = "rez_pip_boy"

version = "3.1.0"

description = "Convert an installed pip package back into a source package"

authors = [
    "Colin Kennedy",
]

help = [["README", "README.md"]]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items bin python"

requires = ["python-2.7+<3.10", "rez-2.47+<3", "rez_utilities-3+<4", "wurlitzer-2+<4"]

_common_run_on = ["default", "pre_release"]

tests = {
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-23+<25"],
        "run_on": _common_run_on,
    },
    "black": {
        "command": "black python tests",
        "requires": ["black-23+<25"],
        "run_on": "explicit",
    },
    "coverage": {
        "command": (
            "coverage erase "
            "&& coverage run --parallel-mode -m unittest discover "
            "&& coverage combine --append "
            "&& coverage html"
        ),
        "requires": ["coverage-5+<6", "mock-3+<4", "six-1.14+<2"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "isort --profile black package.py python tests",
        "requires": ["isort-5.11+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --profile black --check-only --diff package.py python tests",
        "requires": ["isort-5.11+<6"],
        "run_on": _common_run_on,
    },
    "pydocstyle": {
        # Need to disable D202 for now, until a new pydocstyle version is released
        # Reference: https://github.com/psf/black/issues/1159
        #
        "command": "pydocstyle --ignore=D213,D202,D203,D406,D407 python tests/*",
        "requires": ["pydocstyle-6+<7"],
        "run_on": _common_run_on,
    },
    "pylint": {
        # TODO: These --disable flags require deprecating Python 2. Once Python
        # 2 is deprecated, add the flags back in.
        #
        "command": "pylint --disable=super-with-arguments,useless-object-inheritance,consider-using-f-string,raise-missing-from,consider-using-assignment-expr python/rez_pip_boy tests",
        "requires": ["pylint-2.17+<4"],
        "run_on": _common_run_on,
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": ["mock-3+<5", "python-2", "six-1.14+<2",],
        "run_on": _common_run_on,
    },
    "unittest_python_3.9": {
        "command": "python -m unittest discover",
        "requires": ["python-3.9", "six-1.14+<2",],
        "run_on": _common_run_on,
    },
}

uuid = "a1ad023d-c7f3-49be-a3e8-250be6590699"


def commands():
    import os
    import platform

    env.PATH.append(os.path.join("{root}", "bin"))
    env.PYTHONPATH.append(os.path.join("{root}", "python"))

    tar_location = os.getenv("PIP_BOY_TAR_LOCATION", "")

    if not tar_location:
        if any(platform.win32_ver()):
            env.PIP_BOY_TAR_LOCATION.set(r"C:\tarred_rez_packages")
        else:
            env.PIP_BOY_TAR_LOCATION.set(os.path.join("/tmp", "tarred_rez_packages"))
