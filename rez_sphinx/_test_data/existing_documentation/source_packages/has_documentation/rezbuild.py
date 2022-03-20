"""Copy the documentation to the installed package.

This is technically an optional step in the :ref:`rez_sphinx` process. The
documentation doesn't actually have to be copied to the installed package. It
just has to exist on the source Rez package.

"""

import os
import shutil


def main(source_root, destination_root):
    source = os.path.join(source_root, "documentation")
    destination = os.path.join(destination_root, "documentation")

    if os.path.isfile(destination) or os.path.islink(destination):
        os.remove(destination)
    elif os.path.isdir(destination):
        shutil.rmtree(destination)

    shutil.copytree(source, destination)


if __name__ == "__main__":
    main(os.environ["REZ_BUILD_SOURCE_PATH"], os.environ["REZ_BUILD_INSTALL_PATH"])
