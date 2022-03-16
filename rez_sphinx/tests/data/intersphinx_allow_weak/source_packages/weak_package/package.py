name = "weak_package"

version = "1.1.0"


# Copy to the other, inner folder. Just to make installation easier
with scope("config") as config:
    import os

    current_path = os.path.realpath(".")
    root = os.path.dirname(os.path.dirname(current_path))
    config.local_packages_path = os.path.join(root, "installed_packages")


build_command = ""
