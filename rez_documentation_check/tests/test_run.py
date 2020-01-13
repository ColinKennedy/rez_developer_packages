#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that all features of this Python API / CLI work as expected."""

import itertools
import logging
import os
import subprocess
import tempfile
import textwrap
import unittest

from rez import build_process_, build_system, packages_, resolved_context
from rez.config import config
from rez_documentation_check import cli
from rez_documentation_check.core import configuration, sphinx_convention
from rez_utilities import inspection, url_help

from . import common

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_THIS_PACKAGE = inspection.get_nearest_rez_package(_CURRENT_DIRECTORY)
_LOGGER = logging.getLogger(__name__)


class Url(common.Common):
    """Check that different Sphinx conf.py files all return results correctly."""

    @staticmethod
    def _fake_package_root():
        os.environ["REZ_MY_FAKE_PACKAGE_ROOT"] = "blah"

    def _test(self, directory):
        """Get documentation URL links that are missing for a given Rez package file.

        Args:
            directory (str): The absolute path to a Rez package's root directory.

        Returns:
            set[tuple[int, str, str]]:
                The position, help command label, and URL for each invalid URL found.

        """
        self.add_item(directory)
        self._fake_package_root()

        return cli.find_intersphinx_links({directory})

    def test_empty_001(self):
        """Check that setting ``intersphinx_mapping`` to something invalid returns gracefully."""
        self.assertFalse(self._test(_make_fake_package(mapping=None)))

    def test_empty_002(self):
        """Check that setting ``intersphinx_mapping`` to an empty dict works."""
        self.assertFalse(self._test(_make_fake_package(mapping=[])))

    def test_empty_003(self):
        """Check that setting ``intersphinx_mapping`` to missing works."""
        self.assertFalse(self._test(_make_fake_package(mapping=None)))

    def test_missing(self):
        """Check that setting ``intersphinx_mapping`` to missing works."""
        self.assertFalse(self._test(_make_fake_package()))

    def test_no_errors(self):
        """Check that the tool does not error when we expect it pass."""
        self.assertFalse(
            self._test(_make_fake_package([["home-page", "https://google.com"]]))
        )


class Integration(common.Common):
    """Test the command-line execution of ``rez-documentation-check`` and the Python API."""

    def _setup_packages(self):
        """Create fake Rez packages for other unittests."""
        dependency = "foo_bar"
        expected_help = [["api", "https://some_path.com"]]
        dependency_package = _create_fake_rez_dependency_package(
            dependency, help_=expected_help
        )
        importer_package, importer_python_file = _make_importer_package(
            textwrap.dedent(
                """
                for _ in range(10):
                    another()

                    try:
                        from foo_bar import some_module
                    except ImportError:
                        pass
                """
            ),
            dependencies={dependency},
        )
        directory = _make_temporary_build(_THIS_PACKAGE)
        self.add_item(directory)
        importer_root = os.path.dirname(os.path.dirname(importer_package.filepath))
        dependency_root = os.path.dirname(os.path.dirname(dependency_package.filepath))
        self.add_items({importer_root, dependency_root})

        return (
            (directory, importer_root, dependency_root),
            importer_package,
            importer_python_file,
        )

    def test_one_error_001(self):
        """Check that calling the tool from commmand-line contains only a single error.

        Run ``rez-documentation-check`` from command-line (in a subprocess).

        Raises:
            RuntimeError: If the called command-line tool fails for any reason.

        """
        paths, importer_package, importer_python_file = self._setup_packages()
        local_request = "{package.name}=="
        package_paths = list(paths) + config.packages_path  # pylint: disable=no-member

        context = resolved_context.ResolvedContext(
            [_THIS_PACKAGE.name, local_request.format(package=importer_package)],
            package_paths=package_paths,
        )

        # This section is a bit complex. Basically, if a user was
        # running rez-documentation-check, normally every dependency of
        # a package would either already be released or a part of the
        # user's packages. To mimic this assumption, we need to define
        # REZ_PACKAGES_PATH to include the importer_package's path +
        # foo_bar, which is one of its dependenices.
        #
        command = _make_check_command(importer_package, importer_python_file)
        base = "REZ_PACKAGES_PATH={packages_path}".format(
            packages_path=(os.pathsep).join(package_paths)
        )

        process = context.execute_shell(
            command=base + " " + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if stderr:
            raise RuntimeError(stderr)

        expected = (
            'Rez package "foo_bar" has "(\'https://some_path.com\', None)".\n'
            "{   'foo_bar': ('https://some_path.com', None)}\n"
            "Missing intersphinx links were found.\n"
        )

        self.assertTrue(expected in stdout)

    def test_one_error_002(self):
        """Check that the tool contains a single missing intersphinx mapping.

        This test assumes that the user is calling
        ``rez_documentation_check`` along with the other package that
        they're calling from.

        In other words, every imported dependency is already known
        before ``rez-documentation-check`` is ever run.

        """
        dependency = "foo_bar"
        url = "https://some_path.com"

        environment, paths, importer_package, importer_python_file = _make_full_fake_environment(
            {dependency: url}
        )
        self.add_items(paths)

        self._fake_sourcing_the_package(environment, importer_package)

        expected = {importer_package.name: {dependency: (url, None)}}
        self.assertEqual(
            dict(),
            cli.get_existing_intersphinx_links(
                os.path.dirname(importer_package.filepath)
            ),
        )
        self.assertEqual(expected, cli.find_intersphinx_links({importer_python_file}))
        self.assertEqual(
            {dependency: (url, None)},
            cli.get_missing_intersphinx_mappings(
                importer_package, {importer_python_file}
            ),
        )

    def test_multiple_errors(self):
        """Check that the tool contains more than one error."""
        dependency1 = "foo_bar"
        dependency2 = "another_one"
        url1 = "https://some_path.com"
        url2 = "https://another_path_here.com"

        environment, paths, importer_package, importer_python_file = _make_full_fake_environment(
            {dependency1: url1, dependency2: url2}
        )
        self.add_items(paths)

        self._fake_sourcing_the_package(environment, importer_package)

        expected = {
            importer_package.name: {
                dependency1: (url1, None),
                dependency2: (url2, None),
            }
        }
        self.assertEqual(
            dict(),
            cli.get_existing_intersphinx_links(
                os.path.dirname(importer_package.filepath)
            ),
        )
        self.assertEqual(expected, cli.find_intersphinx_links({importer_python_file}))
        self.assertEqual(
            {dependency1: (url1, None), dependency2: (url2, None)},
            cli.get_missing_intersphinx_mappings(
                importer_package, {importer_python_file}
            ),
        )

    def test_partial_errors(self):
        """Check existing intersphinx mapping URLs aren't present in errors."""
        dependency1 = "foo_bar"
        dependency2 = "another_one"
        url1 = "https://some_path.com"
        url2 = "https://another_path_here.com"

        existing_intersphinx = {"fake_environment": ("http:/some_url.com", None)}
        environment, paths, importer_package, importer_python_file = _make_full_fake_environment(
            {dependency1: url1, dependency2: url2},
            existing_intersphinx=existing_intersphinx,
        )
        self.add_items(paths)

        self._fake_sourcing_the_package(environment, importer_package)

        expected = {
            importer_package.name: {
                dependency1: (url1, None),
                dependency2: (url2, None),
            }
        }
        self.assertEqual(
            existing_intersphinx,
            cli.get_existing_intersphinx_links(
                os.path.dirname(importer_package.filepath)
            ),
        )
        self.assertEqual(expected, cli.find_intersphinx_links({importer_python_file}))
        links = {dependency1: (url1, None), dependency2: (url2, None)}
        links.update(existing_intersphinx)
        self.assertEqual(
            links,
            cli.get_missing_intersphinx_mappings(
                importer_package, {importer_python_file}
            ),
        )

    def test_non_api_documentation(self):
        """Find Sphinx documentation, even if it isn't labelled as API documentation."""
        contents = textwrap.dedent(
            """\
            name = "some_package"

            version = "1.0.0"

            description = "A package with help information"

            help = [
                ["some_documentation", "https://google.com"],
                ["another_one", "https://sphinx-code-include.readthedocs.io/en/latest"],
            ]
            """
        )
        directory = tempfile.mkdtemp()
        root = os.path.join(directory, "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(contents)

        self.add_item(directory)

        package = inspection.get_nearest_rez_package(root)

        self.assertEqual(
            "https://sphinx-code-include.readthedocs.io/en/latest/objects.inv",
            url_help.find_package_documentation(package),
        )


class InputIssues(unittest.TestCase):
    """Test incorrect input will raise exceptions as expected."""

    @staticmethod
    def _test_command(command):
        """Run rez-documentation-check in a fake command-line environment.

        Args:
            command (str):
                The rez-documentation-check command that would run on command-line.

        Returns:
            tuple[str, str]: The stdout and stderr that was created by the given `command`.

        """
        context = resolved_context.ResolvedContext([_THIS_PACKAGE.name, "python-2"])
        process = context.execute_shell(
            command=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        return process.communicate()

    def test_missing_package(self):
        """Every file/folder must exist and must be inside of Rez packages."""
        with self.assertRaises(EnvironmentError):
            cli.find_intersphinx_links({"/blah"})

        command = 'rez-documentation-check check --package "" --items "/does/not/exist"'
        stdout, stderr = self._test_command(command)
        expected = (
            "usage: __main__.py check [-h] [-i ITEMS [ITEMS ...]] [-p PACKAGE] [-s] "
            "[-e [EXCLUDED_PACKAGES [EXCLUDED_PACKAGES ...]]] [-a] [-n]\n"
            "__main__.py check: error: argument -p/--package: expected one argument\n"
        ).split()

        self.assertEqual("", stdout)
        self.assertEqual(expected, stderr.split())

    def test_non_rez_input(self):
        """Every file/folder must exist and must be inside of Rez packages."""
        with self.assertRaises(EnvironmentError):
            cli.find_intersphinx_links({"/blah"})

        command = _make_check_command("", "/path/that/does/not/exist")
        _, stderr = self._test_command(command)
        expected = (
            'RuntimeError: Item "/path/that/does/not/exist" resolved to '
            '"/path/that/does/not/exist" but this path does not exist.'
        )

        self.assertTrue(stderr.startswith("Traceback (most recent call last):"))
        self.assertTrue(stderr.rstrip().endswith(expected))


class Others(common.Common):
    """Any test that doesn't fall under existing categories."""

    def test_existing_links(self):
        """Check that the :func:`get_existing_intersphinx_links` works as expected."""
        directory = tempfile.mkdtemp()
        self.add_item(directory)

        source = os.path.join(directory, "documentation", "source")
        os.makedirs(source)

        with open(os.path.join(source, "conf.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """
                    project = "something"
                    release = version = "1.0.0"
                    intersphinx_mapping = {"foo": ("https://cat.com", None)}
                    """
                )
            )

        intersphinx_mapping = {"foo": ("https://cat.com", None)}
        self.assertEqual(
            intersphinx_mapping, cli.get_existing_intersphinx_links(directory)
        )


def _create_fake_rez_dependency_package(name, help_=common.DEFAULT_CODE):
    directory = os.path.join(
        tempfile.mkdtemp(suffix="package_{name}".format(name=name)), name
    )
    contents = textwrap.dedent(
        """\
        name = "{name}"

        version = "1.0.0"

        description = "fake package"

        def commands():
            import os

            env.PYTHONPATH.append(os.path.join("{{root}}", "python"))
        """
    )

    if help_ != common.DEFAULT_CODE:
        contents += "\nhelp = {help_!r}"

    os.makedirs(os.path.join(directory, "python", name))

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(contents.format(name=name, help_=help_))

    open(os.path.join(directory, "python", name, "__init__.py"), "a").close()
    open(os.path.join(directory, "python", name, "some_module.py"), "a").close()

    return packages_.get_developer_package(directory)


def _make_check_command(package, path):
    try:
        directory = os.path.dirname(package.filepath)
    except AttributeError:
        directory = package

    if directory:
        return 'rez-documentation-check check --package {package} --items "{path}"'.format(
            package=directory, path=path
        )

    return 'rez-documentation-check check --items "{path}"'.format(path=path)


def _make_fake_package(mapping=common.DEFAULT_CODE):
    """Create a fake Rez package.

    Args:
        mapping (dict[str] or NoneType, optional):
            Whatever value is given will be added to the generated
            conf.py as the ``intersphinx_mapping`` attribute. If nothing
            is given, ``intersphinx_mapping`` will not be added at all.
            Default: :attr:`common.DEFAULT_CODE`.

    Returns:
        str: The root directory to a Rez package.

    """
    package_code = textwrap.dedent(
        """\
        name = "my_fake_package"

        version = "1.0.0"

        description = "A fake Rez package"

        authors = [
            "Me",
        ]
        """
    )

    directory = os.path.join(
        tempfile.mkdtemp(prefix="rez_documentation_check"), "my_fake_package"
    )
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(package_code)

    common.make_sphinx_files(directory, mapping)
    common.make_python_package(directory)

    return os.path.join(directory, "python")


def _make_full_fake_environment(dependencies, existing_intersphinx=None):
    def _make_importer_code(dependencies):
        base = textwrap.dedent(
            """
            for _ in range(10):
                another()
            """
        )
        template = textwrap.dedent(
            """
            try:
                from {dependency} import some_module
            except ImportError:
                pass
            """
        )

        for dependency in dependencies:
            base += template.format(dependency=dependency)

        return base

    paths = set()
    code = _make_importer_code(dependencies)

    for dependency, url in dependencies.items():
        dependency_package = _create_fake_rez_dependency_package(
            dependency, help_=[["api", url]]
        )
        paths.add(os.path.dirname(os.path.dirname(dependency_package.filepath)))

    importer_package, importer_python_file = _make_importer_package(
        code,
        dependencies=list(dependencies.keys()),
        existing_intersphinx=existing_intersphinx,
    )
    directory = _make_temporary_build(_THIS_PACKAGE)

    local_request = "{package.name}=="
    package_paths = itertools.chain(
        [directory, os.path.dirname(os.path.dirname(importer_package.filepath))],
        paths,
        config.packages_path,  # pylint: disable=no-member
    )
    context = resolved_context.ResolvedContext(
        [_THIS_PACKAGE.name, local_request.format(package=importer_package)],
        package_paths=package_paths,
    )

    environment = context.get_environ()

    return (
        environment,
        {directory, os.path.dirname(os.path.dirname(importer_package.filepath))},
        importer_package,
        importer_python_file,
    )


def _get_build_file_code():
    """str: A generic Bez-style build Python file."""
    code = textwrap.dedent(
        '''\
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-

        """Create helpful functions for building Rez packages, using Python."""

        import os
        import shutil


        def build(source, destination, items):
            """Copy or symlink all items in `source` to `destination`.

            Args:
                source (str):
                    The absolute path to the root directory of the Rez package.
                destination (str):
                    The location where the built files will be copied or symlinked from.
                items (iter[str]):
                    The local paths to every item in `source` to copy / symlink.

            """
            shutil.rmtree(destination)  # Clean any old build folder
            os.makedirs(destination)

            for item in items:
                source_path = os.path.join(source, item)
                destination_path = os.path.join(destination, item)

                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination_path)
                elif os.path.isfile(source_path):
                    shutil.copy2(source_path, destination_path)


        if __name__ == "__main__":
            build(
                os.environ["REZ_BUILD_SOURCE_PATH"],
                os.environ["REZ_BUILD_INSTALL_PATH"],
                {"python", },
            )
        '''
    )

    return code


def _make_importer_package(code, dependencies=None, existing_intersphinx=None):
    if not dependencies:
        dependencies = set()

    contents = textwrap.dedent(
        """\
        name = "importer_package"

        version = "1.0.0"

        description = "A fake Rez package that has at least one dependency."

        build_command = "python {{root}}/rezbuild.py {{install}}"

        requires = [
        {requires}
        ]
        """
    )

    requires = "\n".join(
        '    "{requirement}",'.format(requirement=requirement)
        for requirement in dependencies
    )

    directory = os.path.join(
        tempfile.mkdtemp(suffix="importer_package"), "importer_package"
    )
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(contents.format(requires=requires))

    with open(os.path.join(directory, "rezbuild.py"), "w") as handler:
        handler.write(_get_build_file_code())

    inner_python_directory = os.path.join(directory, "python", "importer_package")
    os.makedirs(inner_python_directory)
    open(os.path.join(inner_python_directory, "__init__.py"), "a").close()

    importer_python_file = os.path.join(inner_python_directory, "some_file.py")

    with open(importer_python_file, "w") as handler:
        handler.write(code)

    package = packages_.get_developer_package(directory)

    if existing_intersphinx:
        documentation = os.path.join(directory, "documentation", "source")
        os.makedirs(documentation)

        text = textwrap.dedent(
            """\
            project = "importer_package"

            version = "1.0"

            release = "1.0.0"

            intersphinx_mapping = {existing_intersphinx!r}
            """
        )

        with open(
            os.path.join(documentation, sphinx_convention.SETTINGS_FILE), "w"
        ) as handler:
            handler.write(text.format(existing_intersphinx=existing_intersphinx))

    return package, importer_python_file


def _make_temporary_build(package):
    working_directory = os.path.dirname(package.filepath)

    system = build_system.create_build_system(
        working_directory, package=package, verbose=True
    )

    # create and execute build process
    builder = build_process_.create_build_process(
        "local",  # See :func:`rez.build_process_.get_build_process_types` for possible values
        working_directory,
        build_system=system,
        verbose=True,
    )

    install_path = tempfile.mkdtemp(
        suffix="package_{package.name}".format(package=package)
    )

    _LOGGER.debug('Building to "%s" path.', install_path)

    with configuration.get_context():
        builder.build(clean=True, install=True, install_path=install_path)

    return install_path
