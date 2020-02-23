#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile
import textwrap
import git

from rez_utilities import creator, inspection
from rez_utilities_git import testify
from python_compatibility.testing import common
from six.moves import mock


# class AddToAttribute(unittest.TestCase):
#     pass
#
#
# class Bump(unittest.TestCase):
#     pass


# class MoveImports(unittest.TestCase):
#     pass


class Yaml2Py(common.Common):
    def _make_fake_released_packages(self):
        root = tempfile.mkdtemp(suffix="_test_replace_yaml")
        self.delete_item_later(root)

        packages = [
            _make_rez_package(
                "some_package",
                textwrap.dedent(
                    """\
                    name: some_package
                    version: 1.2.0
                    description: "A YAML-based package that will be converted."
                    build_command: "echo 'foo'"
                    """
                ),
                root,
            ),
            _make_rez_package(
                "another_package",
                textwrap.dedent(
                    """\
                    name: another_package
                    version: 1.2.0
                    description: "A package.py Rez package that won't be converted."
                    build_command: "echo 'foo'"
                    """
                ),
                root,
            ),
        ]

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

        return repository.working_dir

    # def test_no_replace(self):
    #     pass

    def test_replace_yaml(self):
        """Replace one package.yaml with package.py and don't touch the other package."""
        root = self._make_fake_released_packages()
        command = "rez_batch_process run yaml2py"

        # TODO : Check that the number of times that fix was called is only once

        # self.assertEquals({"package.py", _get_package_files(root)})

    # def test_replace_yaml_multiple(self):
    #     pass


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


def _make_rez_package(name, text, root):
    directory = os.path.join(root, name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.yaml"), "w") as handler:
        handler.write(text)

    print('DIR', directory)
    return inspection.get_nearest_rez_package(directory)
