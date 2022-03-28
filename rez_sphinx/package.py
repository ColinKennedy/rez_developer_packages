name = "rez_sphinx"

version = "1.0.0"

description = "Automate the initialization and building of Sphinx documentation."

# TODO : Make sure this goes to a real path
help = [["README", "README.md"]]

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

@late()
def requires():
    from rez.config import config

    output = [
        "PyYAML-5.4+<7",
        "Sphinx-1.8+<4",
        "python-2.7+<3.8",
        "rez-2.42+<3",
        "rez_bump-1.5+<2",
        "rez_industry-3.1+<4",  # TODO : Kill this awful dependency later
        "rez_python_compatibility-2.8+<3",
        "rez_utilities-2.6+<3",
        "schema-0.7+<1",
        "six-1.15+<2",
    ]

    # 2. Add extra requires, from the user's configuration
    for request_ in config.optionvars.get("rez_sphinx", dict()).get("extra_requires", []):
        if request_ in output:
            continue

        output.append(request_)

    if not in_context():
        return output

    # TODO : Ask the group for a cleaner way of handling this
    if request.get(".rez_sphinx.feature.docbot_plugin", "").endswith("1"):
        output.append("rez_docbot-1+<2")

    return output


variants = [
    ["python-2", "backports.functools_lru_cache-1.6+<2", "mock-3+<4"],
    ["python-3.6+<4"],  # `unittest.mock` was added in Python 3.3+
]

build_command = "python -m rez_build_helper --items bin python"

tests = {
    "black": {
        "command": "black python tests",
        "requires": ["black-22.1+<23"],
        "run_on": "explicit",
    },
    "black_diff": {
        "command": "black --diff --check python tests",
        "requires": ["black-22+<23"],
    },
    "build_documentation": {
        "command": "rez_sphinx build run",
        "requires": [
            # TODO : Add python-3 back in, later
            # "python-3+",  # Get the latest Sphinx / python combination
            "sphinx_rtd_theme-1+<2",
        ],
    },
    "isort": {
        "command": "isort python tests",
        "requires": ["isort-5.9+<6"],
        "run_on": "explicit",
    },
    "isort_check": {
        "command": "isort --check-only --diff --recursive python tests",
        "requires": ["isort-5.9+<6"],
    },
    "pydocstyle": {
        # Need to disable D417 for now, until a new pydocstyle version is released
        #
        # Reference: https://github.com/PyCQA/pydocstyle/blob/master/docs/release_notes.rst
        #
        "command": "pydocstyle --ignore=D213,D203,D406,D407,D417 python tests/*",
        "requires": ["pydocstyle-6.1+<7"],
    },
    # TODO : Add configuration files for these changes. And isort and pydocstyle
    # TODO : Remove "fixme", later
    "pylint": {
        "command": "pylint --disable=use-dict-literal,use-list-literal,bad-continuation,consider-using-f-string,super-with-arguments,useless-object-inheritance,raise-missing-from,fixme python/rez_sphinx tests",
        "requires": ["pylint-2.12+<3"],
    },
    "unittest_python_2": {
        "command": "python -m unittest discover",
        "requires": [
            "python-2",
            "sphinx_rtd_theme-1+<2",
        ],
    },
    "unittest_python_3": {
        "command": "python -m unittest discover",
        "requires": [
            "python-3",
            "sphinx_rtd_theme-1+<2",
        ],
    },
}

uuid = "bea3e936-644e-4e82-b0f1-4bec37db58cc"


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
