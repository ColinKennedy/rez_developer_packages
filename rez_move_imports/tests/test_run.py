#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of unittests for the CLI of ``rez_move_imports``."""

import atexit
import functools
import os
import shutil
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
from rez_move_imports import cli


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

    def test_relative_imports_without_context(self):
        """Try to handle relative imports, if possible, even without a proper Python environment.

        Ideally :mod:`rez_move_imports` should only be run in a context
        where all paths are available on the PYTHONPATH. Sometimes you
        can't do that though (either for speed or complexity reasons).
        Because if this isn't the case, relative imports cannot be resolved
        into absolute imports.

        But if you can't get everything available in the PYTHONPATH then
        a fallback mechanism can be used to "guess" the import structure
        based on the other found Python files.

        Important:
            This fallback assumes that the Rez package only defines one
            common root path for all Python files (it's a big assumption
            but almost always this is the case).

        """
        directory = tempfile.mkdtemp(suffix="_test_relative_imports_without_context")
        atexit.register(functools.partial(shutil.rmtree, directory))

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from old_dependency import a_module

            from . import another_module

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

            from . import another_module

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)


class Deprecation(unittest.TestCase):
    """Make sure deprecation logic works as expected."""

    def test_extras_001(self):
        """Avoid deprecating a Rez package because at least one import remains."""
        directory = tempfile.mkdtemp(suffix="_test_replace_and_no_deprecate")
        atexit.register(functools.partial(shutil.rmtree, directory))

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from old_dependency import a_module
            from old_dependency.a_module import some_function_name
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
            '"{directory} old_dependency.a_module,a_new_namespace.somewhere_else --partial"'
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
            from a_new_namespace.somewhere_else import some_function_name
            from old_dependency import another_import

            def something():
                pass
            """
        )

        with open(some_module, "r") as handler:
            code = handler.read()

        self.assertEqual(expected_code, code)

    def test_extras_002(self):
        """Avoid deprecating a Rez package because at least one import remains."""
        directory = tempfile.mkdtemp(suffix="_test_replace_and_no_deprecate")
        atexit.register(functools.partial(shutil.rmtree, directory))

        some_module = os.path.join(directory, "some_module_inside.py")
        text = textwrap.dedent(
            """\
            # some module with stuff in it

            import os
            import textwrap

            from shared.subpackage import a_module
            from shared.subpackage.a_module import some_function_name
            from shared.subpackage import another_import

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
            '"{directory} shared.subpackage.a_module,shared.new_subpackage.a_module --partial"'
            "".format(directory=directory),
            '--requirements="a_new_package-2+<4,shared.new_subpackage.a_module"',
            '--deprecate="old_dependency_package,shared.subpackage.a_module,shared.subpackage"',
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

            from shared.new_subpackage import a_module
            from shared.new_subpackage.a_module import some_function_name
            from shared.subpackage import another_import

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
