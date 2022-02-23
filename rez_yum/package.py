name = "rez_yum"

version = "1.0.0"

description = "Download RPM packages, using YUM"

authors = ["ColinKennedy"]

private_build_requires = ["rez_build_helper-1+<2"]

requires = [
    "python-2.7+<4",
    "rez-2.104+<3",
    "rez_python_compatibility-2.7+<3",
]

tests = {
    "unittest": "python -m unittest discover",
}

build_command = "python -m rez_build_helper --items bin python"


def commands():
    import os

    env.PATH.append(os.path.join(root, "bin"))
    env.PYTHONPATH.append(os.path.join(root, "python"))
