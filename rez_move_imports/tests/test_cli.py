#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of unittests for the CLI of ``rez_move_imports``."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap

from python_compatibility import wrapping
from python_compatibility.testing import common
from rez_move_imports import cli
from rez_move_imports.core import exception


class Invalids(common.Common):
    """Check that different CLI options fail in predictable ways."""

    def test_bump_conflict(self):
        """Fail argument parsing when --no-bump and --force-requirements-bump are used."""
        directory = tempfile.mkdtemp(suffix="_test_bump_conflict")
        atexit.register(functools.partial(shutil.rmtree, directory))

        command = [
            r'"{directory} "foo,bar""'.format(directory=directory),
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--requirements="second_new_package-1+<2,second.location"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--deprecate="some_another_package,another_thing"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

    def test_no_deprecate(self):
        """Don't run the command if the user doesn't provide at least one package to replace."""
        command = [
            '". old_dependency.a_module,a_new_namespace.somewhere_else"',
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--package-directory="/something/else"',
        ]

        with wrapping.capture_pipes() as output:
            try:
                cli.main(command)
            except SystemExit:
                pass

        _, stderr = output
        expected = "-d DEPRECATE"
        self.assertIn(expected, stderr)
        self.assertTrue(stderr.startswith("usage: "))

    def test_no_requirement(self):
        """Don't run the command if the user doesn't provide requirements to replace with."""
        command = [
            '". old_dependency.a_module,a_new_namespace.somewhere_else"',
            '--package-directory="/something/else"',
        ]

        with wrapping.capture_pipes() as output:
            try:
                cli.main(command)
            except SystemExit:
                pass

        _, stderr = output
        expected = "-r REQUIREMENTS"
        self.assertIn(expected, stderr)
        self.assertTrue(stderr.startswith("usage: "))

    def test_invalid_deprecate(self):
        """Defining --deprecate but missing either the Rez package for namespaces must error."""
        command = [
            '". something,new_thing"',
            '--requirements="some_package,new_thing"',
            '--deprecate="an_invalid_thing_here"',
        ]

        with self.assertRaises(exception.InvalidInput):
            cli.main(command)

    def test_invalid_requirement(self):
        """Defining --requirements but missing either the Rez package for namespaces must error."""
        command = [
            '". something,new_thing"',
            '--requirements="some_package,new_thing"',
            '--deprecate="an_invalid_thing_here"',
        ]

        with self.assertRaises(exception.InvalidInput):
            cli.main(command)

    def test_no_association(self):
        """Every old and new namespace pairs should have a Rez package associated with them."""
        directory = tempfile.mkdtemp(suffix="_test_no_replace_and_no_deprecate")
        self.delete_item_later(directory)

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from old_dependency import a_module

            def something():
                pass
            """
        )

        with open(some_module, "w") as handler:
            handler.write(text)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_test_package"
                    """
                )
            )

        command = [
            '"{directory} something,new_thing"'.format(directory=directory),
            '--requirements="some_package,new_thing"',
            '--deprecate="another_package,a_namespace_that_should_have_been_something"',
        ]

        with self.assertRaises(exception.MissingNamespaces):
            cli.main(command)

    def test_missing_directory(self):
        """If a package directory is given and it doesn't exist, fail early."""
        directory = tempfile.mkdtemp(suffix="_test_missing_directory")
        self.delete_item_later(directory)

        shutil.rmtree(directory)

        command = [
            '"{directory} something,new_thing"'.format(directory=directory),
            '--requirements="some_package,new_thing"',
            '--deprecate="another_package,a_namespace_that_should_have_been_something"',
            "--package-directory",
            '"{directory}"'.format(directory=directory),
        ]

        with self.assertRaises(exception.MissingDirectory):
            cli.main(command)

    def test_invalid_directory(self):
        """If an existing package directory is given but has no Rez package."""
        directory = tempfile.mkdtemp(suffix="_test_missing_directory")

        command = [
            '"{directory} something,new_thing"'.format(directory=directory),
            '--requirements="some_package,new_thing"',
            '--deprecate="another_package,a_namespace_that_should_have_been_something"',
            "--package-directory",
            '"{directory}"'.format(directory=directory),
        ]

        with self.assertRaises(exception.InvalidDirectory):
            cli.main(command)


class Options(common.Common):
    """Check that different CLI options work as we expect."""

    def test_deprecate_and_replace_multiple(self):
        """Replace more than one package with more than one new package(s) at once."""
        directory = tempfile.mkdtemp(suffix="_test_deprecate_and_replace_multiple")
        self.delete_item_later(directory)

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from another_thing.stuff import some_module
            from old_dependency import a_module

            def something():
                pass
            """
        )

        with open(some_module, "w") as handler:
            handler.write(text)

        package = os.path.join(directory, "package.py")

        with open(package, "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_test_package"

                    version = "1.1.0"

                    requires = [
                        "old_dependency_package-1+<3",
                        "python-2",
                        "some_another_package-2",
                        "something_more",
                    ]
                    """
                )
            )

        command = [
            r'"{directory} "old_dependency.a_module,a_new_namespace.somewhere_else:another_thing,second.location" --partial"'  # pylint: disable=line-too-long
            "".format(directory=directory),
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--requirements="second_new_package-1+<2,second.location"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--deprecate="some_another_package,another_thing"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "1.2.0"

            requires = [
                "a_new_package-2+<4",
                "python-2",
                "second_new_package-1+<2",
                "something_more",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)

        expected_code = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from second.location.stuff import some_module
            from a_new_namespace import somewhere_else

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)

    def test_force_requirements_bump(self):
        """Bump the required version, even if no namespaces were replaced."""
        directory = tempfile.mkdtemp(suffix="_test_force_requirements_bmp")
        atexit.register(functools.partial(shutil.rmtree, directory))

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            def something():
                pass
            """
        )

        with open(some_module, "w") as handler:
            handler.write(text)

        package = os.path.join(directory, "package.py")

        with open(package, "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_test_package"

                    version = "3.2"

                    requires = [
                        "dependency_package-1.3+<2",
                        "something_more",
                        "python-2",
                    ]
                    """
                )
            )

        command = [
            '"{directory} old_dependency.does_not_exist,old_dependency.does_not_exist_zz"'
            "".format(directory=directory),
            '--requirements="dependency_package-2+<3,old_dependency.does_not_exist_zz"',
            '--deprecate="dependency_package,old_dependency.does_not_exist"',
            '--package-directory="{directory}"'.format(directory=directory),
            "--force-requirements-bump",
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "3.3"

            requires = [
                "dependency_package-2+<3",
                "something_more",
                "python-2",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)

        expected_code = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)

    def test_no_bump(self):
        """Don't bump the Rez package version, even if changes to the package were made."""
        directory = tempfile.mkdtemp(suffix="_test_replace_and_deprecate")
        self.delete_item_later(directory)

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from old_dependency import a_module

            def something():
                pass
            """
        )

        with open(some_module, "w") as handler:
            handler.write(text)

        package = os.path.join(directory, "package.py")

        with open(package, "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_test_package"

                    version = "3.2.build_13"

                    requires = [
                        "something_more",
                        "old_dependency_package-1+<3",
                        "python-2",
                    ]
                    """
                )
            )

        command = [
            '"{directory} old_dependency.a_module,a_new_namespace.somewhere_else"'
            "".format(directory=directory),
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
            "--no-bump",
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "3.2.build_13"

            requires = [
                "a_new_package-2+<4",
                "something_more",
                "python-2",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)

        expected_code = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from a_new_namespace import somewhere_else

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)
