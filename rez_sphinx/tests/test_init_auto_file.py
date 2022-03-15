"""Make sure any auto-generated documentation files are made, correctly."""

import contextlib
import os
import textwrap
import unittest

from rez_utilities import finder

from .common import package_wrap, run_test


class General(unittest.TestCase):
    """Make sure any auto-generated documentation files are made, correctly."""

    def test_custom_files(self):
        """Define and generate a custom file, on :doc:`init_command`."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)
        name = "some_custom_file"
        expected_body = "Some example text"

        with _override_default_files([{"base_text": expected_body, "path": name}]):
            run_test.test(["init", directory])

        path = os.path.join(directory, "documentation", "source", name + ".rst")

        with open(path, "r") as handler:
            custom_file_data = handler.read().splitlines(keepends=False)

        master_index = os.path.join(directory, "documentation", "source", "index.rst")

        with open(master_index, "r") as handler:
            master_data = handler.read()

        master_data = _get_base_master_index_text(
            os.path.join(directory, "documentation", "source", "index.rst")
        )

        header = custom_file_data[0]
        body = custom_file_data[-1]

        self.assertEqual(
            textwrap.dedent(
                """\
                Welcome to some_package's documentation!
                ========================================

                .. toctree::
                   :maxdepth: 2
                   :caption: Contents:

                   some_custom_file


                Indices and tables
                ==================

                * :ref:`genindex`
                * :ref:`modindex`
                * :ref:`search`"""
            ),
            master_data,
        )

        self.assertEqual("Some Custom File", header)
        self.assertEqual(expected_body, body)

    def test_default_files(self):
        """Make sure :ref:`rez_sphinx` makes example starting files for the user."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)
        run_test.test(["init", directory])

        developer = os.path.join(
            directory, "documentation", "source", "developer_documentation.rst"
        )

        with open(developer, "r") as handler:
            developer_text = handler.read()

        user = os.path.join(
            directory, "documentation", "source", "user_documentation.rst"
        )

        with open(user, "r") as handler:
            user_text = handler.read()

        master_text = _get_base_master_index_text(
            os.path.join(directory, "documentation", "source", "index.rst")
        )

        self.assertEqual(
            textwrap.dedent(
                """\
                User Documentation
                ==================

                ..
                    rez_sphinx_help:User Documentation

                This auto-generated file is meant to be written by the developer. Please
                provide anything that could be useful to the reader such as:

                - General Overview
                - A description of who the intended reader is (developers, artists, etc)
                - Tutorials
                - "Cookbook" style tutorials
                - Table Of Contents (toctree) to other Sphinx pages
                """
            ),
            user_text,
        )
        self.assertEqual(
            textwrap.dedent(
                """\
                Developer Documentation
                =======================

                ..
                    rez_sphinx_help:Developer Documentation

                This auto-generated file is meant to be written by the developer. Please
                provide anything that could be useful to the reader such as:

                - General Overview
                - A description of who the intended reader is (developers, artists, etc)
                - Tutorials
                - "Cookbook" style tutorials
                - Table Of Contents (toctree) to other Sphinx pages
                """
            ),
            developer_text,
        )
        self.assertEqual(
            textwrap.dedent(
                """\
                Welcome to some_package's documentation!
                ========================================

                .. toctree::
                   :maxdepth: 2
                   :caption: Contents:

                   developer_documentation
                   user_documentation


                Indices and tables
                ==================

                * :ref:`genindex`
                * :ref:`modindex`
                * :ref:`search`"""
            ),
            master_text,
        )

    def test_enforce_non_default_text(self):
        """Forbid documentation building if they haven't modified their files.

        Todo:
            Add a unittest to disable this feature, if the user chooses to.

        """
        raise ValueError()

    def test_no_files(self):
        """Make sure users can opt-out of the default files, if they wish."""
        package = package_wrap.make_simple_developer_package()
        directory = finder.get_package_root(package)

        with _override_default_files([]):
            run_test.test(["init", directory])

        for path in [
            os.path.join(
                directory, "documentation", "source", "developer_documentation.rst"
            ),
            os.path.join(
                directory, "documentation", "source", "user_documentation.rst"
            ),
        ]:
            self.assertFalse(
                os.path.isfile(path),
                msg='Path "{path}" exists.'.format(path=path),
            )


def _get_base_master_index_text(path):
    """Get the text from ``path`` but without any top-level Sphinx comments.

    Args:
        path (str): The absolute or relative path to a Sphinx `index.rst`_ on disk.

    Raises:
        RuntimeError: If the document body could not be found.

    Returns:
        str: The document body of ``path``.

    """
    with open(path, "r") as handler:
        lines = handler.read().splitlines()

    found = -1

    for index, line in enumerate(lines):
        if line.startswith("Welcome to "):
            found = index

            break
    else:
        raise RuntimeError("No title line was found")

    return "\n".join(lines[found:])


@contextlib.contextmanager
def _override_default_files(files):
    """Use ``files`` when running :doc:`init_command` instead of the defaults.

    Args:
        files (list[dict[str, str or bool]]):
            The description of each default file to create.
            See :attr:`.FILE_ENTRY` for details.

    Yields:
        context: The temporary environment.

    """
    with run_test.keep_config() as config:
        config.optionvars["rez_sphinx"] = dict()
        config.optionvars["rez_sphinx"]["init_options"] = dict()
        config.optionvars["rez_sphinx"]["init_options"]["default_files"] = files

        yield
