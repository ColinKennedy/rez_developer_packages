#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that the plugin commands the ``rez_batch_plugins`` defines work as-expected."""

import functools
import os
import shlex
import sys
import tempfile
import textwrap

from python_compatibility.testing import common
from rez_batch_plugins.plugins import yaml2py
from rez_batch_process.core import registry, worker
from rez_utilities import creator, inspection, rez_configuration
from rez_utilities_git import testify
from six.moves import mock

# class AddToAttribute(unittest.TestCase):
#     pass
#
#
# class Bump(unittest.TestCase):
#     pass


# class MoveImports(unittest.TestCase):
#     def test_no_change(self):
#         pass
#
#     def test_single_change(self):
#         pass
#
#     def test_multiple_change(self):
#         pass


class Yaml2Py(common.Common):
    """Check that the :mod:`rez_batch_plugins.plugins.yaml2py` plugin works correctly."""

    @classmethod
    def setUpClass(cls):
        """Add some generic plugins so that tests have something to work with."""
        super(Yaml2Py, cls).setUpClass()

        _clear_registry()
        yaml2py.main()

    @classmethod
    def tearDownClass(cls):
        """Remove all stored plugins."""
        super(Yaml2Py, cls).tearDownClass()

        _clear_registry()

    def _make_fake_released_packages(self, other_package):
        """Create 2 basic Rez packages to use for testing.

        Args:
            other_package (str):
                If "yaml", one of the packages created will be a
                package.yaml file. Otherwise, it gets added as a
                package.py file.

        Returns:
            str: The path where all of the created packages will go to.

        """
        root = tempfile.mkdtemp(suffix="_test_replace_yaml")
        self.delete_item_later(root)

        packages = [
            _make_rez_package(
                "another_package",
                "package.py",
                textwrap.dedent(
                    """\
                    name = "another_package"
                    version = "1.2.0"
                    description = "A package.py Rez package that won't be converted."
                    build_command = "echo 'foo'"
                    """
                ),
                root,
            )
        ]

        if other_package == "yaml":
            packages.append(
                _make_rez_package(
                    "some_package",
                    "package.yaml",
                    textwrap.dedent(
                        """\
                        name: some_package
                        version: 1.2.0
                        description: "A YAML-based package that will be converted."
                        build_command: "echo 'foo'"
                        """
                    ),
                    root,
                )
            )
        else:
            packages.append(
                _make_rez_package(
                    "some_package",
                    "package.py",
                    textwrap.dedent(
                        """\
                        name = "some_package"
                        version = "1.2.0"
                        description = "A YAML-based package that will be converted."
                        build_command = "echo 'foo'"
                        """
                    ),
                    root,
                )
            )

        repository, packages, remote_root = testify.make_fake_repository(packages, root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        release_path = tempfile.mkdtemp(suffix="_some_release_location")
        self.delete_item_later(release_path)

        options, parser = _make_fake_release_data()

        for package in packages:
            creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
                search_paths=[repository.working_dir],
                quiet=True,
            )

        return release_path

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )
    def test_no_replace(self, _create_pull_request):
        """Don't replace anything because no package is package.yaml."""
        release_path = self._make_fake_released_packages("py")

        text = shlex.split("run yaml2py fake_pr_prefix fake-github-access-token")
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            unfixed, invalids, skips = _get_test_results("yaml2py")

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [
                ("another_package", "is not a package.yaml file."),
                ("some_package", "is not a package.yaml file."),
            ],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        self.assertEqual(0, _create_pull_request.call_count)

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )
    def test_replace_yaml(self, _create_pull_request):
        """Replace one package.yaml with package.py and don't touch the other package."""
        release_path = self._make_fake_released_packages("yaml")

        text = shlex.split("run yaml2py fake_pr_prefix fake-github-access-token")
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            unfixed, invalids, skips = _get_test_results("yaml2py")

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [("another_package", "is not a package.yaml file.")],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        self.assertEqual(1, _create_pull_request.call_count)


def _clear_registry():
    for name in registry.get_plugin_keys():
        registry.clear_plugin(name)

    for name in registry.get_command_keys():
        registry.clear_command(name)


def _make_fake_release_data():
    """Make the required arguments needed for rez-release to work."""
    options = mock.MagicMock()
    options.cmd = "release"
    options.debug = False
    options.message = "Fake release message"
    options.no_message = False
    options.process = "local"
    options.variants = None
    options.vcs = None

    parser = mock.MagicMock()
    parser.prog = "rez release"

    return options, parser


def _make_package_with_modules(name, modules, root):
    template = textwrap.dedent(
        """\
        name = "{name}"

        version = "1.2.0"

        build_command = "echo 'foo'"

        def commands():
            import os

            env.PYTHONPATH.append(os.path.join("{{root}}", "python"))
        """
    )

    directory = os.path.join(root, name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(template.format(name=name))

    for path, text in modules:
        full_path = os.path.join(root, path)
        path_directory = os.path.dirname(full_path)

        if path_directory and not os.path.isdir(path_directory):
            os.makedirs(path_directory)

        with open(full_path, "w") as handler:
            handler.write(text)

    return inspection.get_nearest_rez_package(directory)


def _make_rez_package(name, package_name, text, root):
    """Create a package.py or package.yaml Rez package file.

    Args:
        name (str): The Rez package family name.
        package_name (str): Use "package.py" or "package.yaml" here.
        text (str): The contents of the created file.
        root (str): A directory where the newly created file will be written to.

    Returns:
        :class:`rez.packages_.DeveloperPackage`: The generated Rez package.

    """
    directory = os.path.join(root, name)
    os.makedirs(directory)

    with open(os.path.join(directory, package_name), "w") as handler:
        handler.write(text)

    return inspection.get_nearest_rez_package(directory)


def _get_test_results(command_text, paths=None):
    """Get the conditions for a test (but don't actually run unittest.

    Args:
        command_text (str):
            Usually "shell", "yaml2py", "move_imports", etc. This string
            will find and modify Rez packages based on some registered
            plugin.
        paths (list[str], optional):
            The locations on-disk that will be used to any
            Rez-environment-related work. Some plugins need these paths
            for resolving a context, for example. Default is None.

    Returns:
        The output of :func:`rez_batch_process.core.worker.run`.

    """
    arguments = mock.MagicMock()

    finder = registry.get_package_finder(command_text)
    valid_packages, invalid_packages, skips = finder(paths=paths)

    command = registry.get_command(command_text)

    _, unfixed, invalids = worker.run(
        functools.partial(command.run, arguments=arguments), valid_packages
    )

    invalids.extend(invalid_packages)

    return (unfixed, invalids, skips)
