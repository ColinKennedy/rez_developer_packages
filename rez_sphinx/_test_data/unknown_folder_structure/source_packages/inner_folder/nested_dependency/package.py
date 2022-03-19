name = "nested_dependency"

version = "1.0.0"

requires = ["another_nested-1", "pure_dependency-1"]

build_command = ""

with scope("config") as config:
    import os

    _CURRENT_DIRECTORY = os.path.dirname(os.path.realpath("."))
    parent = os.path.dirname(os.path.dirname(_CURRENT_DIRECTORY))
    root = os.path.join(parent, "installed_packages")
    config.local_packages_path = root
    config.packages_path = [config.local_packages_path]
