"""Make sure :ref:`rez_sphinx publish` works as expected."""

import io
import os
import textwrap
import unittest

from rez_utilities import creator, finder, rez_configuration
from python_compatibility import wrapping
from six.moves import mock

from ..common import package_wrap, run_test


class Run(unittest.TestCase):
    """Make sure :ref:`rez_sphinx publish run` works as expected."""

    def test_no_build_documentation_key(self):
        """Allow publishing even if there's no :ref:`build_documentation_key`."""
        source_package = _make_package_with_no_tests_attribute()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_no_build_documentation_key")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

        # :ref:`rez_sphinx init` adds to `tests`_ by default. So we
        # explicitly disable the tests as soon as that process is complete.
        #
        _disable_tests(source_directory)
        source_package = finder.get_nearest_rez_package(
            finder.get_package_root(source_package)
        )
        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve(
            [installed_package]
        ), wrapping.silence_printing(), run_test.allow_defaults(), mock.patch(
            "rez_sphinx.commands.publish_run.get_all_publishers"
        ) as patch:
            patch.return_value = []  # Prevent actually attempting to publish

            run_test.test(
                ["publish", "run", source_directory, "--packages-path", install_path]
            )

    def test_not_inited(self):
        """Fail publishing because :ref:`rez_sphinx init` was never ran."""
        raise ValueError()


def _disable_tests(directory):
    with io.open(
        os.path.join(directory, "package.py"), "a", encoding="utf-8"
    ) as handler:
        handler.write("\n\ntests = {}")


def _make_package_with_no_tests_attribute():
    """rez.packages.Package: A source Rez package with no `tests`_ attribute."""
    return package_wrap.make_simple_developer_package(
        textwrap.dedent(
            """\
            name = "some_package"

            version = "1.0.0"

            requires = ["python"]

            build_command = "python {root}/rezbuild.py"
            """
        )
    )
