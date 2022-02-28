"""Make sure :ref:`rez_sphinx build` works as expected."""

import contextlib
import os
import sys
import unittest
import textwrap

from rez_utilities import creator, finder

from .common import package_wrap, run_test


class Build(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build` works as expected."""

    def test_hello_world(self):
        """Build documentation and auto-API .rst documentation onto disk."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory(
            "Build_test_hello_world_install_root"
        )
        installed_package = creator.build(source_package, install_path)

        with _simulate_resolve(installed_package):
            run_test.test(["init", source_directory])
            run_test.test(["build", source_directory])

        source = os.path.join(source_directory, "documentation", "source")
        api_source_gitignore = os.path.join(source, "api", ".gitignore")
        source_master = os.path.join(source, "index.rst")

        master_toctrees = ["\n".join(tree) for tree in _get_toctrees(source_master)]
        build = os.path.join(source_directory, "documentation", "build")
        build_master = os.path.join(build, "index.html")
        example_api_path = os.path.join(build, "api", "file.html")

        self.assertEqual(1, len(master_toctrees))
        self.assertEqual(
            textwrap.dedent(
                """\
                .. toctree::
                   :maxdepth: 2
                   :caption: Contents:

                   API Documentation <api/modules.rst>"""
            ),
            master_toctrees[0],
        )
        self.assertTrue(os.path.isfile(api_source_gitignore))
        self.assertTrue(os.path.isfile(build_master))
        self.assertTrue(os.path.isfile(example_api_path))

    def test_hello_world_other_folder(self):
        """Build documentation again, but from a different PWD."""
        raise ValueError()

    def test_intersphinx_loading(self):
        """Make sure sphinx.ext.intersphinx "sees" Rez packages as expected."""
        raise ValueError()


class Options(unittest.TestCase):
    """Make sure options (CLI, rez-config, etc) work as expected."""

    def test_auto_api_config(self):
        """Build API documentation because the rez-config says to."""
        raise ValueError()

    def test_auto_api_explicit(self):
        """Build API documentation because the CLI flag was explicitly added."""
        raise ValueError()

    def test_auto_api_implicit(self):
        """Auto-build API documentation if no CLI flag or Rez config option is set."""
        raise ValueError()

    def test_auto_api_implicit_pass(self):
        """Don't auto-build API documentation if no CLI / config / auto-detect.

        If all systems fail, just warn the user in a log and build
        documentation as normal. It would just mean that the user didn't want
        to have auto-documentation.

        """
        raise ValueError()

    def test_generate_api_config(self):
        """Build API documentation because the rez-config says to."""
        raise ValueError()

    def test_generate_api_explicit(self):
        """Build API documentation because the CLI flag was explicitly added."""
        raise ValueError()

    def test_generate_api_implicit(self):
        """Auto-build API documentation if no CLI flag or Rez config option is set."""
        raise ValueError()

    def test_generate_api_implicit_pass(self):
        """Don't auto-build API documentation if no CLI / config / auto-detect.

        If all systems fail, just warn the user in a log and build
        documentation as normal. It would just mean that the user didn't want
        to have auto-documentation.

        """
        raise ValueError()


class Invalid(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build` fails when expected."""

    def test_bad_permissions(self):
        """Fail building if the user lacks permissions to write to-disk."""
        raise ValueError()

    def test_no_package(self):
        """Fail early if no Rez package was found."""
        raise ValueError()

    def test_no_source(self):
        """Fail early if documentation source does not exist."""
        raise ValueError()

    def test_auto_api_no_python_files(self):
        """Fail to auto-build API .rst files if there's no Python files."""
        raise ValueError()


def _get_toctrees(path):
    """Get every :ref:`toctree` in ``path``.

    Args:
        path (str): The absolute or relative path to a Sphinx .rst file.

    Returns:
        list[list[str]]: Each :ref:`toctree` as a list of lines.

    """
    def _get_indent(text):
        return len(text) - len(text.lstrip())

    def _trim(tree):
        count = 0

        for index in reversed(range(len(tree))):
            if tree[index].strip():
                break

            count += 1

        return tree[: -1 * count]

    with open(path, "r") as handler:
        data = handler.read()

    start = False
    trees = []
    current = []
    last_indent = 0

    for line in data.splitlines():
        if line.startswith(".. toctree::"):
            start = True
            current.append(line)

            continue

        if not start:
            continue

        if not line.strip():
            current.append(line)

            continue

        indent = _get_indent(line)

        if indent < last_indent:
            last_indent = -1
            start = False
            trimmed = _trim(current)
            trees.append(trimmed)
            current = []
        else:
            last_indent = indent
            current.append(line)

    return trees


@contextlib.contextmanager
def _simulate_resolve(installed_package):
    """Make a resolve with ``installed_package`` and :ref:`rez_sphinx`."""
    root = finder.get_package_root(installed_package)
    directory = os.path.join(root, "python")

    if not os.path.isdir(directory):
        raise RuntimeError(
            'Directory "{directory}" does not exist.'.format(directory=directory)
        )

    original_environment = os.environ.copy()
    original_path = sys.path[:]

    # TODO : Do a Rez API call here, instead
    os.environ["REZ_{name}_ROOT".format(name=installed_package.name.upper())] = root
    sys.path.append(directory)

    try:
        yield
    finally:
        sys.path = original_path
        os.environ.clear()
        os.environ.update(original_environment)
