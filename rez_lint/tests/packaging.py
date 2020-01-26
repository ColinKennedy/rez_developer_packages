#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A set of basic classes and functions to make unittesting for ``rez_lint`` a bit easier."""

import contextlib
import os
import tempfile

from python_compatibility.testing import common
from rez import packages_
from rez.config import config
from rez_utilities import creator, inspection


class BasePackaging(common.Common):
    """A simple class for testing in ``rez_lint``. Its job is to make Rez installed packages."""

    def _make_installed_package(self, name, text, packages_path=None):
        """Create a Rez source package and install it into a temporary directory.

        All temporary directories will be marked for clean-up. Clean-up
        occurs after each test is run.

        Args:
            name (str):
                The name of the source Rez packge to create.
            text (str):
                The text that will be used for a "package.py" file.
            packages_path (list[str], optional):
                The paths that will be used to search for Rez packages while
                building. This is usually to make it easier to find package
                dependencies. If `packages_path` is not defined, Rez will
                use its default paths. Default is None.

        Returns:
            :class:`rez.developer_package.DeveloperPackage`:
                The package the represents the newly-built package.

        """
        directory = make_fake_source_package(name, text)

        package = packages_.get_developer_package(directory)
        new_package = creator.build(
            package, tempfile.mkdtemp(), packages_path=packages_path
        )

        self.add_item(os.path.dirname(directory))
        self.add_item(inspection.get_packages_path_from_package(new_package))

        return new_package


def make_fake_source_package(name, text):
    """Create a Rez source package using the given `name`.

    Args:
        name (str): The name of the source Rez packge to create.
        text (str): The text that will be used for a "package.py" file.

    Returns:
        str: The directory on-disk that points to the root of the Rez package.

    """
    directory = os.path.join(tempfile.mkdtemp("_some_rez_source_package"), name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(text)

    return directory


@contextlib.contextmanager
def override_packages_path(paths, prepend=False):
    """Change the :attr:`rez.config.packages_path` attribute to whatever `paths` is.

    Example:
        >>> with override_packages_path(["/foo/bar"], prepend=True):
        ...     some_command_that_relies_on_the_rez_api()

    Args:
        paths (list[str]):
            The new paths that will be used to search for Rez packages.
        prepend (bool, optional):
            If False, `paths` will completely override :attr:`rez.config.packages_path`.
            If True, `paths` will be given priority over :attr:`rez.config.packages_path`
            but the original packages_path will stick around. Default is False.

    """
    original = list(config.packages_path)  # pylint: disable=no-member

    if prepend:
        config.packages_path[:] = paths + original  # pylint: disable=no-member
    else:
        config.packages_path[:] = paths  # pylint: disable=no-member

    try:
        yield
    finally:
        config.packages_path[:] = original  # pylint: disable=no-member
