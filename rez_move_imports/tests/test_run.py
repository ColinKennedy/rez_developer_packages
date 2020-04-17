#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of unittests for the CLI of ``rez_move_imports``."""

import os
import shutil
import tempfile
import textwrap

from python_compatibility import wrapping
from python_compatibility.testing import common
from rez_move_imports import cli
from rez_move_imports.core import exception


class Bugs(common.Common):
    """A series of tests for any unexpected bugs that come up while using ``rez_move_imports``."""

    def test_replace_from_no_requirements(self):
        """When the original Rez package has no requirements, it causes Rez to fail.

        This test makes sure that doesn't cause problems for ``rez_move_imports``.

        """
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
                    # -*- coding: utf-8 -*-

                    name = "a_package_here"

                    version = "1.3.0"

                    build_command = "echo 'foo'"

                    def commands():
                        import os

                        env.PYTHONPATH.append('asdf')
                    """
                )
            )

        command = [
            '"{directory} old_dependency.a_module,a_new_namespace.somewhere_else"'
            "".format(directory=directory),
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            # -*- coding: utf-8 -*-

            name = "a_package_here"

            version = "1.4.0"

            requires = [
                "a_new_package-2+<4",
            ]

            build_command = "echo 'foo'"

            def commands():
                import os

                env.PYTHONPATH.append('asdf')
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


class Invalids(common.Common):
    """Check that different CLI options fail in predictable ways."""

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
        expected = "usage: python -m unittest [-h] -r REQUIREMENTS -d DEPRECATE [-n] [-p PACKAGE_DIRECTORY] command\npython -m unittest: error: argument -d/--deprecate is required\n"  # pylint: disable=line-too-long

        self.assertEqual(expected, stderr)

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
        expected = "usage: python -m unittest [-h] -r REQUIREMENTS -d DEPRECATE [-n] [-p PACKAGE_DIRECTORY] command\npython -m unittest: error: argument -r/--requirements is required\n"  # pylint: disable=line-too-long

        self.assertEqual(expected, stderr)

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


class Integrations(common.Common):
    """Make sure the CLI works as-expected."""

    def test_no_replace_and_no_deprecate(self):
        """Don't replace any imports because none of the namespaces are found.

        And since no namespaces were changed, the Rez package.py should, either.

        """
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
            '--deprecate="another_package,something"',
        ]
        cli.main(command)

        with open(some_module, "r") as handler:
            unchanged_code = handler.read()

        self.assertEqual(text, unchanged_code)

    def test_replace_and_deprecate(self):
        """Replace the imports of the Python modules in a package and then change the package."""
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
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "3.3.build_13"

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

    def test_replace_and_no_deprecate(self):
        """Replace the imports of the Python modules in a package but don't change the package.

        We don't deprecate the original package because there
        is still an import tied to the package that we tried to
        deprecate in-use. And because it's there, we cannot replace
        old_dependency_package.

        """
        directory = tempfile.mkdtemp(suffix="_test_replace_and_no_deprecate")
        self.delete_item_later(directory)

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from old_dependency import a_module
            from old_dependency import another_import

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

                    version = "1.0.0"

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
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "1.1.0"

            requires = [
                "a_new_package-2+<4",
                "something_more",
                "old_dependency_package-1+<3",
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
            from old_dependency import another_import

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)

    def test_allow_weird_input(self):
        """Make sure --deprecate works, even if it is accidentally given version information."""
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

                    version = "99.98.99"

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
            '--deprecate="old_dependency_package-1+<3,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "99.99.0"

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

    def test_replace_same_family(self):
        """If --deprecate and --requirements specify the same package, replace with --requirements.

        The reason why we do this is for a very specific scenario.
        If you have a Rez package whose version must be bumped to a later version
        in response to some recent changes.

        Maybe package_a-2.0 has functions moved to package_b so you want
        to replace the imports of package_c, which depends on package_a,
        to use package_a-2.0 (which was originally on package_a-1.3) and
        replace any old package_a-1.3 imports with its new location in
        package_b.

        """
        directory = tempfile.mkdtemp(suffix="_test_replace_and_no_deprecate")
        self.delete_item_later(directory)

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from old_dependency import a_module
            from old_dependency import another_import

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

                    version = "1.0.0"

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
            '--requirements="old_dependency_package-2+<4,old_dependency"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "1.1.0"

            requires = [
                "a_new_package-2+<4",
                "old_dependency_package-2+<4",
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
            from old_dependency import another_import

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)
