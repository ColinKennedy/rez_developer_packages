import contextlib
import unittest

from rez_utilities import creator, finder
import six
from rez_sphinx.core import hook

from .common import package_wrap, run_test


class HelpScenarios(unittest.TestCase):
    def test_escaped_colon(self):
        # - When converting "Tagged" Sphinx .rst files, add a unittest to make sure ":" is escapable. Since ":" is also the delimiter
        raise ValueError()

    def test_ref_role(self):
        ".. _foo:"
        # - If the .. rez_sphinx comment (tag) is above a sphinx ref like .. _foo::, include that anchor in the text when it gets added to rez-help
        raise ValueError()


class AppendHelp(unittest.TestCase):
    def test_string(self):
        raise ValueError()

    def test_list(self):
        raise ValueError()

    def test_none(self):
        # 1. Build the initial Rez package
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        # 2. Initialize the documentation
        run_test.test(["init", directory])

        install_path = package_wrap.make_directory("_AppendHelp_test_none")

        # 3a. Simulate adding the pre-build hook to the user's Rez configuration.
        # 3b. Re-build the Rez package so it can auto-append entries to the package.py ``help``
        #
        with _override_preprocess():
            creator.build(package, install_path, quiet=True)
            raise ValueError(install_path)


@contextlib.contextmanager
def _override_preprocess():
    with run_test.keep_config() as config:
        config.package_preprocess_function = hook.package_preprocess_function

        yield
