name = "guessable_package"

version = "1.0.0"

requires = ["pure_dependency-1"]

# Blah nested_dependency - This should be picked up when we run --suggestion-mode=guess

build_command = ""

with scope("config") as config:
    import os

    _CURRENT_DIRECTORY = os.path.dirname(os.path.realpath("."))
    parent = os.path.dirname(os.path.dirname(_CURRENT_DIRECTORY))
    root = os.path.join(parent, "installed_packages")
    config.local_packages_path = root
    config.packages_path = [config.local_packages_path]
