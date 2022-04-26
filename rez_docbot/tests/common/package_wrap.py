"""Miscellaneous functions for making Rez packages easier."""

import atexit
import functools
import io
import os
import shutil
import tempfile
import textwrap

from rez import developer_package


def make_package_configuration(configuration):
    """Create a Rez `package.py`_ with the given ``configuration``.

    Args:
        configuration (dict[str, object]):
            The override settings to apply to :ref:`rez_sphinx`.

    Returns:
        rez.developer_package.DeveloperPackage: The generated source Rez package.

    """
    directory = tempfile.mkdtemp(suffix="_make_package_config")
    atexit.register(functools.partial(shutil.rmtree, directory))

    template = textwrap.dedent(
        """\
        name = "foo"

        version = "1.0.0"

        rez_docbot_configuration = {configuration!r}
        """
    )

    with io.open(
        os.path.join(directory, "package.py"),
        "w",
        encoding="utf-8",
    ) as handler:
        handler.write(template.format(configuration=configuration))

    return developer_package.DeveloperPackage.from_path(directory)


def make_temporary_directory(suffix):
    """str: Make a folder on-disk using ``suffix``."""
    directory = tempfile.mkdtemp(suffix=suffix)
    atexit.register(functools.partial(shutil.rmtree, directory))

    return directory
