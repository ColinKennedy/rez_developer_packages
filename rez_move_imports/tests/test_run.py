#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import textwrap
import unittest

from rez_move_imports import cli
from python_compatibility.testing import common
# TODO : Add unittests that checks for bad arguments
# TODO : Need 2 unittests for --use-pythonpath. One where it doesn't do a replace because the module isn't in the right spot and one that does


class Integrations(common.Common):
    def test_no_replace_and_no_deprecate(self):
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
            ''.format(directory=directory),
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
            '--package-directory="{directory}"'.format(directory=directory),
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

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

                    requires = [
                        "something_more",
                        "old_dependency_package-1+<3",
                        "python-2",
                    ]
                    """
                )
            )

        command = [
            '"{directory}"'.format(directory=directory),
            '--namespaces=old_dependency.a_module,a_new_namespace.somewhere_else',
            '--requirements="a_new_package-2+<4,a_new_namespace"',
            '--deprecate="old_dependency_package,old_dependency"',
        ]

        cli.main(command)

        expected_package = textwrap.dedent(
            """\
            name = "some_test_package"

            requires = [
                "something_more",
                "old_dependency_package-1+<3",
                "a_new_package-2+<4",
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
