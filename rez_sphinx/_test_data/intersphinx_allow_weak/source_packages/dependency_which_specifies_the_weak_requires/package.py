name = "dependency_which_specifies_the_weak_requires"

version = "7.0.0"

# Copy to the other, inner folder. Just to make installation easier
with scope("config") as config:
    import os

    current_path = os.path.realpath(".")
    root = os.path.dirname(os.path.dirname(current_path))
    config.local_packages_path = os.path.join(root, "installed_packages")
    config.packages_path = [config.local_packages_path]

requires = ["weak_package-1+"]

build_command = ""
