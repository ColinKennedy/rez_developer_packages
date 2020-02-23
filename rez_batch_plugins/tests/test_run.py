#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that the plugin commands the ``rez_batch_plugins`` defines work as-expected."""

import os
import subprocess
import sys
import shlex
from rez_batch_process import cli
import tempfile
import textwrap

import functools
from rez_batch_process.core import registry, worker

import git
from rez_batch_plugins.plugins import yaml2py
from python_compatibility.testing import common
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
    @classmethod
    def setUpClass(cls):
        """Add some generic plugins so that tests have something to work with."""
        super(Yaml2Py, cls).setUpClass()

        for name in registry.get_plugin_keys():
            registry.clear_plugin(name)

        for name in registry.get_command_keys():
            registry.clear_command(name)

        registry.register_plugin("yaml2py", yaml2py._get_non_python_packages)
        registry.register_command("yaml2py", yaml2py.Yaml2Py)

    @classmethod
    def tearDownClass(cls):
        """Remove all stored plugins."""
        super(Yaml2Py, cls).tearDownClass()

        for name in registry.get_plugin_keys():
            registry.clear_plugin(name)

        for name in registry.get_command_keys():
            registry.clear_command(name)

    def _make_fake_released_packages(self, other_package):
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
            ),
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

    @staticmethod
    def _test_unhandled(paths=None):
        """Get the conditions for a test (but don't actually run unittest.

        Args:
            paths (list[str], optional): The locations on-disk that
                will be used to any Rez-environment-related work. Some
                plugins need these paths for resolving a context, for
                example. Default is None.

        Returns:
            The output of :func:`rez_batch_process.core.worker.run`.

        """
        arguments = mock.MagicMock()

        finder = registry.get_package_finder("yaml2py")
        valid_packages, invalid_packages, skips = finder(paths=paths)

        command = registry.get_command("yaml2py")

        _, unfixed, invalids = worker.run(
            functools.partial(command.run, arguments=arguments),
            valid_packages,
        )

        invalids.extend(invalid_packages)

        return (unfixed, invalids, skips)

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request")
    def test_no_replace(self, _create_pull_request):
        """Don't replace anything because no package is package.yaml."""
        release_path = self._make_fake_released_packages("py")

        text = shlex.split("run yaml2py fake_pr_prefix fake-github-access-token")
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            unfixed, invalids, skips = self._test_unhandled()

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

    @mock.patch("rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request")
    def test_replace_yaml(self, _create_pull_request):
        """Replace one package.yaml with package.py and don't touch the other package."""
        release_path = self._make_fake_released_packages("yaml")

        text = shlex.split("run yaml2py fake_pr_prefix fake-github-access-token")
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            unfixed, invalids, skips = self._test_unhandled()

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [("another_package", "is not a package.yaml file.")],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        self.assertEqual(1, _create_pull_request.call_count)


# def _get_package_files(root):
#     # root is a remote repository
#     root =
#     git.Repo.clone
#     atexit =


def _make_fake_release_data():
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


def _make_rez_package(name, package_name, text, root):
    directory = os.path.join(root, name)
    os.makedirs(directory)

    with open(os.path.join(directory, package_name), "w") as handler:
        handler.write(text)

    return inspection.get_nearest_rez_package(directory)
