"""Ensure :ref:`rez_docbot <rez_docbot>` loads and fails as expected."""

import unittest

from python_compatibility import wrapping
from rez_utilities import creator, finder

from rez_sphinx.core import exception

from ..common import package_wrap, run_test


class Loader(unittest.TestCase):
    """Ensure :ref:`rez_docbot <rez_docbot>` loads and fails as expected."""

    def test_publish_run(self):
        """Fail :ref:`rez_sphinx publish run` if :ref:`rez_docbot` is not loaded."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_Loader_test_not_loaded")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing(), run_test.allow_defaults(), self.assertRaises(
                exception.MissingPlugIn
            ):
                run_test.test(["publish", "run", source_directory])

    def test_view_publish_url(self):
        """Fail :ref:`rez_sphinx view publish-url` if ``rez_docbot`` is not loaded."""
        with self.assertRaises(exception.MissingPlugIn):
            run_test.test("view publish-url")
