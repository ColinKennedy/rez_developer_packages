name = "rez_symbl"

version = "1.0.0"

description = "Collect Rez requests into a single folder (for use with REZ_PACKAGES_PATH)"

authors = [
    "Colin Kennedy",
]

private_build_requires = ["rez_build_helper-1+<2"]

build_command = "python -m rez_build_helper --items python"

requires = [
    "rez-2.40+",
    "rez_utilities-1.4+<2",
]


def commands():
    import os

    env.PYTHONPATH.append(os.path.join("{root}", "python"))
