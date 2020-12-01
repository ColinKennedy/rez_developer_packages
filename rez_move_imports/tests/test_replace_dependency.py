#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that dependency-related attributes are replaced as expected."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap
import unittest

from rez_move_imports import cli


class Expansion(unittest.TestCase):
    """Make sure version bumping dependency Rez package versions works as expected."""

    def test_all(self):
        """Expand the minimum and maximum verison of an updated dependency."""
        directory = tempfile.mkdtemp(suffix="_DependencyExpansion_test_all")
        atexit.register(functools.partial(shutil.rmtree, directory))

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
                        "a_new_package-1.7",
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

    def test_keep_maximum(self):
        """Use the existing maximum version because it's higher than the specified version."""
        directory = tempfile.mkdtemp(suffix="_DependencyExpansion_test_all")
        atexit.register(functools.partial(shutil.rmtree, directory))

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
                        "a_new_package-3+<5",
                        "python-2",
                    ]
                    """
                )
            )

        command = [
            '"{directory} old_dependency.a_module,a_new_namespace.somewhere_else"'
            "".format(directory=directory),
            '--requirements="a_new_package-3+<4,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "1.1.0"

            requires = [
                "a_new_package-3+<5",
                "something_more",
                "old_dependency_package-1+<3",
                "python-2",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)

    def test_keep_minimum(self):
        """Use the existing minimum version because it's higher than the specified version."""
        directory = tempfile.mkdtemp(suffix="_DependencyExpansion_test_all")
        atexit.register(functools.partial(shutil.rmtree, directory))

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
                        "a_new_package-3+",
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
                "a_new_package-3+<4",
                "something_more",
                "old_dependency_package-1+<3",
                "python-2",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)

    def test_maximum(self):
        """Expand the maximum verison of an updated dependency."""
        directory = tempfile.mkdtemp(suffix="_DependencyExpansion_test_all")
        atexit.register(functools.partial(shutil.rmtree, directory))

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
                        "a_new_package-2+<3",
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

    def test_minimum(self):
        """Expand the minimum verison of an updated dependency."""
        directory = tempfile.mkdtemp(suffix="_DependencyExpansion_test_all")
        atexit.register(functools.partial(shutil.rmtree, directory))

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
                        "a_new_package-1.7",
                        "python-2",
                    ]
                    """
                )
            )

        command = [
            '"{directory} old_dependency.a_module,a_new_namespace.somewhere_else"'
            "".format(directory=directory),
            '--requirements="a_new_package-2.2,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "1.1.0"

            requires = [
                "a_new_package-2.2",
                "something_more",
                "old_dependency_package-1+<3",
                "python-2",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)

    def test_nothing(self):
        """Expand nothing, because the version is already what it needs to be."""
        directory = tempfile.mkdtemp(suffix="_DependencyExpansion_test_all")
        atexit.register(functools.partial(shutil.rmtree, directory))

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
                        "a_new_package-1+<2.2",
                        "python-2",
                    ]
                    """
                )
            )

        command = [
            '"{directory} old_dependency.a_module,a_new_namespace.somewhere_else"'
            "".format(directory=directory),
            '--requirements="a_new_package-1,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            version = "1.1.0"

            requires = [
                "a_new_package-1+<2.2",
                "something_more",
                "old_dependency_package-1+<3",
                "python-2",
            ]
            """
        )

        with open(package, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_package, code)
