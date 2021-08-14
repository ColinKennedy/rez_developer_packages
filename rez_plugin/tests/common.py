#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helper classes and functions for making unittests easier."""

import os
import sys
import textwrap

from python_compatibility.testing import common
from rez.config import config
from rez_documentation_check.core import sphinx_convention

DEFAULT_CODE = object()


class Common(common.Common):
    """Test-agnostic helper methods."""

    def setUp(self):
        """Store Rez's local paths (because tests may modify it) so it can be restored later."""
        super(Common, self).setUp()

        self._rez_packages_path = list(
            config.packages_path  # pylint: disable=no-member
        )

    def tearDown(self):
        """Restore the old Rez packages_path configuration variable."""
        config.packages_path[:] = self._rez_packages_path  # pylint: disable=no-member

    @staticmethod
    def _fake_sourcing_the_package(environment, package):
        """Pretend to source the Rez package just to make unittests a little faster to run."""
        sys.path[:] = environment["PYTHONPATH"].split(os.pathsep)
        os.environ["REZ_IMPORTER_PACKAGE_ROOT"] = os.path.dirname(package.filepath)


def make_python_package(directory):
    """Make a basic Python package.

    Args:
        directory (str): The created Python package will be placed underneath
            `directory`, an absolute folder.

    """
    package_directory = os.path.join(directory, "python", "my_fake_package")
    os.makedirs(package_directory)
    open(os.path.join(package_directory, "__init__.py"), "a").close()


def make_sphinx_files(directory, mapping=DEFAULT_CODE):
    """Create example Sphinx files for unittesting.

    Args:
        directory (str): The absolute directory to a Rez package.
        mapping (dict[str] or NoneType, optional): Whatever value is given
            will be added to the generated conf.py as the
            ``intersphinx_mapping`` attribute. If nothing is given,
            ``intersphinx_mapping`` will not be added at all.

    """
    source_directory = os.path.join(directory, "documentation", "source")
    os.makedirs(source_directory)

    conf_code = textwrap.dedent(
        """
        # Lots of code

        # More code

        {intersphinx_mapping}

        # And even more
        """
    )

    intersphinx_mapping = ""

    if mapping != DEFAULT_CODE:
        intersphinx_mapping = "intersphinx_mapping = {mapping!r}".format(
            mapping=mapping
        )

    conf_code = conf_code.format(intersphinx_mapping=intersphinx_mapping)

    with open(
        os.path.join(source_directory, sphinx_convention.SETTINGS_FILE), "w"
    ) as handler:
        handler.write(conf_code)
