name = "package_to_test"

version = "2.1.0"

# Copy to the other, inner folder. Just to make installation easier
with scope("config") as config:
    import os

    current_path = os.path.realpath(".")
    root = os.path.dirname(os.path.dirname(current_path))
    config.local_packages_path = os.path.join(root, "installed_packages")
    config.packages_path = [
        os.path.join(root, "installed_packages"),
        # TODO : Make this better, later. We shouldn't be assuming external python comes from a certain path
        os.path.join(os.path.expanduser("~"), "packages"),  # Contains ``python``
    ]

requires = ["python", "some_package-1+"]

build_command = "python {root}/rezbuild.py"

tests = {
    "build_non_standard_documentation": {
        "command": "rez_sphinx build",
        "requires": ["another_package-1+<2", "rez_sphinx-1.0+<2"],
    },
}


def commands():
    import os

    env.PYTHONPATH.append(os.path.join(root, "python"))