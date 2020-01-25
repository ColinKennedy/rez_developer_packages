#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=too-many-lines
"""Test all of the checkers in "dangers.py"."""

import os
import shutil
import tempfile
import textwrap

from rez import packages_
from rez.config import config
from rez_lint import cli
from rez_utilities import creator, inspection
from six.moves import mock

from .. import packaging


class ImproperRequirements(packaging.BasePackaging):
    """Add tests for Rez-requirement related checkers."""

    def test_no_impropers_001(self):
        """Check that a package with no "improper" requirements don't trigger any errors."""
        package = self._make_installed_package(
            "my_package",
            textwrap.dedent(
                """\
                name = "my_package"
                version = "1.0.0"
                build_command = "echo 'foo'"
                """
            ),
        )
        directory = inspection.get_package_root(package)

        results = cli.lint(directory)
        has_issue = any(
            description
            for description in results
            if description.get_summary()[0]
            == "Improper package requirements were found"
        )

        self.assertFalse(has_issue)

    def test_no_impropers_002(self):
        """Adding some dependency should not trigger the "improper" check."""
        dependency_package = self._make_installed_package(
            "some_dependency_that_is_okay",
            textwrap.dedent(
                """\
                name = "some_dependency_that_is_okay"
                version = "1.0.0"
                build_command = "echo 'foo'"
                """
            ),
        )
        dependency_path = inspection.get_packages_path_from_package(dependency_package)

        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = [
            dependency_path
        ] + original  # pylint: disable=no-member

        try:
            installed_package = self._make_installed_package(
                "my_package",
                textwrap.dedent(
                    """\
                    name = "my_package"
                    version = "1.0.0"

                    requires = [
                        "some_dependency_that_is_okay",
                    ]

                    build_command = "echo 'foo'"
                    """
                ),
            )
        except Exception:
            raise
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        directory = inspection.get_package_root(installed_package)
        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = [  # pylint: disable=no-member
            directory,
            dependency_path,
        ] + original

        try:
            results = cli.lint(directory)
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        has_issue = any(
            description
            for description in results
            if description.get_summary()[0]
            == "Improper package requirements were found"
        )

        self.assertFalse(has_issue)

    # TODO : Add support for this later
    # def test_one_improper_001(self):
    #     """If the user has a build system in their variants, flag it as an issue."""
    #     pass
    #
    # def test_one_improper_002(self):
    #     """If the user has a unittest system in their variants, flag it as an issue."""
    #     pass

    def test_multiple_impropers(self):
        """Find multiple improper Rez packages. Build and unittest systems."""
        dependencies = set()
        descriptions = [
            (
                "cmake",
                textwrap.dedent(
                    """\
                    name = "cmake"
                    version = "1.0.0"
                    build_command = "echo 'foo'"
                    """
                ),
            ),
            (
                "some_dependency_that_is_okay",
                textwrap.dedent(
                    """\
                    name = "some_dependency_that_is_okay"
                    version = "1.0.0"
                    build_command = "echo 'foo'"
                    """
                ),
            ),
            (
                "mock",
                textwrap.dedent(
                    """\
                    name = "mock"
                    version = "1.0.0"
                    build_command = "echo 'foo'"
                    """
                ),
            ),
        ]

        for name, code in descriptions:
            package = self._make_installed_package(name, code)
            dependencies.add(inspection.get_packages_path_from_package(package))

        dependencies = list(dependencies)
        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = dependencies + original  # pylint: disable=no-member

        try:
            installed_package = self._make_installed_package(
                "my_package",
                textwrap.dedent(
                    """\
                    name = "my_package"
                    version = "1.0.0"

                    requires = [
                        "cmake",
                        "mock",
                        "some_dependency_that_is_okay",
                    ]

                    build_command = "echo 'foo'"
                    """
                ),
            )
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        directory = inspection.get_package_root(installed_package)
        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = (  # pylint: disable=no-member
            [directory] + dependencies + original
        )

        try:
            results = cli.lint(directory)
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            in (
                "Improper build package requirements were found",
                "Improper unittest package requirements were found",
            )
        ]

        self.assertEqual(2, len(issues))

        self.assertEqual(
            issues[0].get_message(verbose=True)[1].lstrip(),
            "Requirements \"['cmake']\" should not be in requires. "
            "Instead, they should be either defined in the "
            "``private_build_requires`` or ``build_requires`` attribute.",
        )

        self.assertEqual(
            issues[1].get_message(verbose=True)[1].lstrip(),
            "Requirements \"['mock']\" should not be in requires. "
            "Instead, they should be defined as part of the package's ``tests`` attribute.",
        )

    def test_mixed_impropers(self):
        """Have one import dependency, and one okay one."""
        dependencies = set()
        descriptions = [
            (
                "some_dependency_that_is_okay",
                textwrap.dedent(
                    """\
                    name = "some_dependency_that_is_okay"
                    version = "1.0.0"
                    build_command = "echo 'foo'"
                    """
                ),
            ),
            (
                "mock",
                textwrap.dedent(
                    """\
                    name = "mock"
                    version = "1.0.0"
                    build_command = "echo 'foo'"
                    """
                ),
            ),
        ]

        for name, code in descriptions:
            package = self._make_installed_package(name, code)
            dependencies.add(inspection.get_packages_path_from_package(package))

        dependencies = list(dependencies)
        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = dependencies + original  # pylint: disable=no-member

        try:
            installed_package = self._make_installed_package(
                "my_package",
                textwrap.dedent(
                    """\
                    name = "my_package"
                    version = "1.0.0"

                    requires = [
                        "mock",
                        "some_dependency_that_is_okay",
                    ]

                    build_command = "echo 'foo'"
                    """
                ),
            )
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        directory = inspection.get_package_root(installed_package)
        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = (
            [directory] + dependencies + original
        )  # pylint: disable=no-member

        try:
            results = cli.lint(directory)
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Improper unittest package requirements were found"
        ]

        self.assertEqual(1, len(issues))


class MissingRequirements(packaging.BasePackaging):
    """Check that the :class:`rez_lint.plugins.checkers.dangers.MissingRequirements` class works."""

    def _make_nested_dependencies(self):
        """list[str]: A helper function to make some dependencies to test with."""
        code = textwrap.dedent(
            """\
            name = "another_dependency"
            version = "1.0.0"
            requires = []
            build_command = "python {root}/rezbuild.py {install}"

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join("{root}", "python"))
            """
        )

        dependency1_directory = packaging.make_fake_source_package(
            "another_dependency", code
        )
        self.add_item(os.path.dirname(dependency1_directory))

        with open(os.path.join(dependency1_directory, "rezbuild.py"), "w") as handler:
            handler.write(_get_rezbuild_text())

        os.makedirs(os.path.join(dependency1_directory, "python"))

        with open(
            os.path.join(dependency1_directory, "python", "some_module.py"), "w"
        ) as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    def get_foo():
                        return 8
                    """
                )
            )

        dependency1_build_path = tempfile.mkdtemp(suffix="_another_dependency")
        self.add_item(dependency1_build_path)

        creator.build(
            packages_.get_developer_package(dependency1_directory),
            dependency1_build_path,
        )

        code = textwrap.dedent(
            """\
            name = "direct_dependency"
            version = "1.0.0"
            requires = [
                "another_dependency-1",
            ]
            build_command = "python {root}/rezbuild.py {install}"

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join("{root}", "python"))
            """
        )

        dependency2_directory = packaging.make_fake_source_package(
            "direct_dependency", code
        )
        self.add_item(os.path.dirname(dependency2_directory))
        os.makedirs(os.path.join(dependency2_directory, "python"))

        with open(os.path.join(dependency2_directory, "rezbuild.py"), "w") as handler:
            handler.write(_get_rezbuild_text())

        dependency2_build_path = tempfile.mkdtemp(suffix="_direct_dependency")
        self.add_item(dependency2_build_path)

        creator.build(
            packages_.get_developer_package(dependency2_directory),
            dependency2_build_path,
            packages_path=[dependency1_build_path] + config.packages_path,
        )

        return [dependency1_build_path, dependency2_build_path]

    def _create_test_environment(self, text, files=None):
        """Make a Rez source package, given some Rez definition text, for testing.

        Args:
            text (str):
                The text that will be used for a "package.py" file.
            files (iter[str], optional):
                File paths that will be used to create empty files in
                the source package. Default is empty.

        Returns:
            list[:class:`rez_lint.core.message_description.Description`]: Get the found issues.

        """
        if not files:
            files = set()

        directory = packaging.make_fake_source_package("some_package", text)
        self.add_item(os.path.dirname(directory))

        for path in files:
            full_path = os.path.join(directory, path)
            path_directory = os.path.dirname(full_path)

            if not os.path.isdir(path_directory):
                os.makedirs(path_directory)

            open(full_path, "a").close()

        return cli.lint(directory)

    def test_empty(self):
        """Don't error if there is not set of requirements listed."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            """
        )

        results = self._create_test_environment(code)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Missing Package requirements"
        ]

        self.assertEqual([], issues)

    def test_none_001(self):
        """Don't error if there are requirements defined but the list is empty."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = []
            """
        )

        results = self._create_test_environment(code)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Missing Package requirements"
        ]

        self.assertEqual([], issues)

    def test_none_002(self):
        """Don't error if there are requirements defined but the list is empty and there's files."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = []

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join("{root}", "python"))
            """
        )

        results = self._create_test_environment(
            code, files={os.path.join("python", "some_module.py")}
        )

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Missing Package requirements"
        ]

        self.assertEqual([], issues)

    def test_one(self):
        """Error because there is a missing dependency.

        In this case, the Rez package includes "direct_dependency".
        But the import, "import some_module" actually comes from the
        dependency package of "direct_dependency". In other words,
        "some_package" should also depend on "another_dependency", but
        doesn't.

        """
        dependency_paths = self._make_nested_dependencies()

        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = [
                "direct_dependency",
            ]

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join("{root}", "python"))
            """
        )

        root = os.path.join(
            tempfile.mkdtemp(suffix="_some_package_location"), "some_package"
        )
        os.makedirs(root)
        self.add_item(root)
        os.makedirs(os.path.join(root, "python"))

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(code)

        with open(
            os.path.join(root, "python", "a_module_with_dependency.py"), "w"
        ) as handler:
            handler.write("import some_module; print(some_module.get_foo())")

        original = list(config.packages_path)
        config.packages_path[:] = dependency_paths + config.packages_path

        try:
            results = cli.lint(root)
        finally:
            config.packages_path[:] = original

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Missing Package requirements"
        ]

        self.assertEqual(1, len(issues))
        self.assertEqual(
            "Full list \"['another_dependency']\".",
            issues[0].get_message(verbose=True)[-1].lstrip(),
        )

    def test_mixed(self):
        """Get the right missing dependencies even if a mix of dependencies are given."""
        dependency_paths = self._make_nested_dependencies()

        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = [
                "direct_dependency",
                "python",
            ]

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join("{root}", "python"))
            """
        )

        root = os.path.join(
            tempfile.mkdtemp(suffix="_some_package_location"), "some_package"
        )
        os.makedirs(root)
        self.add_item(root)
        os.makedirs(os.path.join(root, "python"))

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(code)

        with open(
            os.path.join(root, "python", "a_module_with_dependency.py"), "w"
        ) as handler:
            handler.write("import some_module; print(some_module.get_foo())")

        original = list(config.packages_path)
        config.packages_path[:] = dependency_paths + config.packages_path

        try:
            results = cli.lint(root)
        finally:
            config.packages_path[:] = original

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Missing Package requirements"
        ]

        self.assertEqual(1, len(issues))
        self.assertEqual(
            "Full list \"['another_dependency']\".",
            issues[0].get_message(verbose=True)[-1].lstrip(),
        )


class RequirementLowerBoundsMissing(packaging.BasePackaging):
    """Test that the :class:`.RequirementLowerBoundsMissing` works as expected."""

    def _test_found(self, name, code):
        """Run a test that assumes that there is a "lower-bounds-missing" issue.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: If `code` has no "lower-bounds-missing" issue
                or the issue isn't a Python issue.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package requires are missing a minimum version"
        ]

        self.assertEqual(1, len(issues))
        self.assertEqual(
            "Requirements \"['python']\" have no minimum version.",
            issues[0].get_message(verbose=True)[-1].lstrip(),
        )

    def _test_not_found(self, name, code):
        """Run a test that assumes that there is no "lower-bounds-missing" issue.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: `code` must result in no ``rez_lint`` "lower-bounds-missing" issue.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package requires are missing a minimum version"
        ]

        self.assertEqual(0, len(issues))

    def test_empty(self):
        """If no ``requires`` is listed, don't raise an issue."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            """
        )

        self._test_not_found("some_package", code)

    def test_none(self):
        """If ``requires`` is listed but it's empty, don't raise an issue."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = []
            """
        )

        self._test_not_found("some_package", code)

    def test_okay(self):
        """If there's no issue, don't raise any issues."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = ["python-2+", "rez-2+"]
            """
        )

        self._test_not_found("some_package", code)

    def test_one(self):
        """If ``requires`` has an issue, raise it."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = ["python"]
            """
        )

        self._test_found("some_package", code)

    def test_mixed(self):
        """If ``requires`` has a mixture of requirements, raise only the problems."""
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            requires = [
                "rez-2+",
                "python",
            ]
            """
        )

        self._test_found("some_package", code)


class RequirementsNotSorted(packaging.BasePackaging):
    """Test the :class:`rez_lint.plugins.checkers.dangers.RequirementsNotSorted.` class."""

    def _test_found(self, name, code, expected):
        """Test a scenario where unsorted requirements are found.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.
            expected (str): The first line of the found issue (after the summary).

        Raises:
            AssertionError: If the issue was not found.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package requirements are not sorted"
        ]

        self.assertEqual(1, len(issues))
        self.assertEqual(
            expected, issues[0].get_message(verbose=True)[-1].lstrip(),
        )

    def _test_not_found(self, name, code):
        """Test a scenario where requirements are sorted.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: If the issue was found.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package requirements are not sorted"
        ]

        self.assertEqual(0, len(issues))

    def test_empty(self):
        """Check that an issue isn't raised if ``requires`` is not defined."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                """
            ),
        )

    def test_none(self):
        """Check that an issue isn't raised if ``requires`` is defined but empty."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = []
                """
            ),
        )

    def test_one_001(self):
        """Check that an issue is raised."""
        self._test_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = ["rez", "python"]
                """
            ),
            "Expected order: \"['python', 'rez']\"",
        )

    def test_one_002(self):
        """Check that an issue is raised."""
        self._test_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = ["rez-2+", "python-2+<3"]
                """
            ),
            "Expected order: \"['python-2+<3', 'rez-2+']\"",
        )

    def test_okay_001(self):
        """Check that an issue is not raised."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = ["python", "rez"]
                """
            ),
        )

    def test_okay_002(self):
        """Check that an issue is not raised."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = ["python-2+<3", "rez-2+"]
                """
            ),
        )


class NotPythonDefinition(packaging.BasePackaging):
    """Test that the :class:`rez_lint.plugins.checkers.dangers.NotPythonDefinition.` class works."""

    def test_yaml(self):
        """Test that package.yaml files trigger an issue."""
        root = os.path.join(tempfile.mkdtemp(suffix="_test_yaml"), "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.yaml"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name: some_package
                    version: 1.0.0
                    """
                )
            )

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Using a non-Python Rez package definition file"
        ]

        self.assertEqual(1, len(issues))

    def test_python(self):
        """Test that package.py files don't trigger an issue."""
        root = os.path.join(tempfile.mkdtemp(suffix="_test_yaml"), "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"
                    version = "1.0.0"
                    """
                )
            )

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Using a non-Python Rez package definition file"
        ]

        self.assertEqual([], issues)


class NoRezTest(packaging.BasePackaging):
    """Test that the :class:`rez_lint.plugins.checkers.dangers.NoRezTest.` class works."""

    def test_undefined(self):
        """Test that undefined rez tests trigger an issue."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package has no rez-test attribute defined"
        ]

        self.assertEqual(1, len(issues))

    def test_empty(self):
        """Test that an empty rez test triggers an issue."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                tests = {}
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package has no rez-test attribute defined"
        ]

        self.assertEqual(1, len(issues))

    def test_exists(self):
        """Test that having 1+ rez tests is enough to satisfy the checker."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                tests = {"some_test": "echo 'I am a test!'"}
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package has no rez-test attribute defined"
        ]

        self.assertEqual([], issues)


class TooManyDependencies(packaging.BasePackaging):
    """Test that the :class:`rez_lint.plugins.checkers.dangers.TooManyDependencies.` class works."""

    def test_undefined(self):
        """Test that having undefined dependencies does not trigger the issue."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0].startswith(
                "Package has too many dependencies ("
            )
        ]

        self.assertEqual([], issues)

    def test_empty(self):
        """Test that having no dependencies does not trigger the issue."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = []
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0].startswith(
                "Package has too many dependencies ("
            )
        ]

        self.assertEqual([], issues)

    def test_under(self):
        """Test that having dependencies does not raise an issue if they're below the maximum."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = ["python"]
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package has too many dependencies (0/10)"
        ]

        self.assertEqual([], issues)

    def test_over(self):
        """Test that having too many dependencies raises an issue."""
        root = packaging.make_fake_source_package(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                requires = [
                    "dependency_1",
                    "dependency_2",
                    "dependency_3",
                    "dependency_4",
                    "dependency_5",
                    "dependency_6",
                    "dependency_7",
                    "dependency_8",
                    "dependency_9",
                    "dependency_10",
                    "dependency_11",
                    ]
                """
            ),
        )
        self.add_item(os.path.dirname(root))

        package_definition_template = textwrap.dedent(
            """\
            name = "{name}"
            version = "1.0.0"
            """
        )

        dependencies = set()

        for index in range(1, 12):
            name = "dependency_{index}".format(index=index)
            directory = packaging.make_fake_source_package(
                name, package_definition_template.format(name=name)
            )
            package = packages_.get_developer_package(directory)
            dependencies.add(inspection.get_packages_path_from_package(package))

            self.add_item(os.path.dirname(directory))

        original = list(config.packages_path)  # pylint: disable=no-member
        config.packages_path[:] = (
            list(dependencies) + original
        )  # pylint: disable=no-member

        try:
            results = cli.lint(root)
        finally:
            config.packages_path[:] = original

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package has too many dependencies (11/10)"
        ]

        self.assertEqual(1, len(issues))


class UrlNotReachable(packaging.BasePackaging):
    """Test that the :class:`rez_lint.plugins.checkers.dangers.UrlNotReachable.` class works."""

    def _test_found(self, name, code):
        """Run a test that assumes that there is a "url-unreachable" issue.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: If `code` doesn't return a "url-unreachable" issue.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package help has an un-reachable URL"
        ]

        self.assertEqual(1, len(issues))

        first_non_summary_line = issues[0].get_message(verbose=True)[-1].lstrip()
        self.assertTrue(
            first_non_summary_line.startswith('Found URLs are un-reachable "')
        )

    def _test_not_found(self, name, code):
        """Run a test that assumes that there is no "url-unreachable" issue.

        Args:
            name (str): The name of the fake Rez source package to create.
            code (str): The source code used to create a package definition.

        Raises:
            AssertionError: If `code` actually does return a "url-unreachable" issue.

        """
        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package help has an un-reachable URL"
        ]

        self.assertEqual([], issues)

    def test_undefined(self):
        """Check that undefined URL(s) is considered "valid" by this checker."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                """
            ),
        )

    def test_empty_001(self):
        """Check that an empty URL is considered "valid" by this checker."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = ""
                """
            ),
        )

    def test_empty_002(self):
        """Check that an empty list of URLs is considered "valid" by this checker."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = []
                """
            ),
        )

    def test_reachable_001(self):
        """Check that regular websites are shown as "reachable"."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = [["Home Page", "https://www.google.com"]]
                """
            ),
        )

    def test_reachable_002(self):
        """Check that IP addresses are shown as "reachable"."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = "http://216.58.192.142"  # This is the IP address of google.com
                """
            ),
        )

    def test_reachable_003(self):
        """Test that having a single ``help`` URL is allowed, as long it's reachable."""
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = "https://www.google.com"
                """
            ),
        )

    def test_reachable_004(self):
        """Test that a relative file path is still allowed (rez-help allows it)."""
        name = "some_package"
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            help = "README.md"
            """
        )

        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))
        open(os.path.join(directory, "README.md"), "a").close()

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package requires are missing a minimum version"
        ]

        self.assertEqual(0, len(issues))

    def test_reachable_005(self):
        """Test that an absolute file path is still allowed (rez-help allows it)."""
        path = tempfile.mkdtemp()
        name = "some_package"
        template = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            help = "{path}"
            """
        )
        code = template.format(path=path)

        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0]
            == "Package requires are missing a minimum version"
        ]

        self.assertEqual(0, len(issues))

    def test_unreachable_001(self):
        """Report an issue if the URL doesn't point to a valid website."""
        self._test_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = "something_that_doesnt_exist.com"
                """
            ),
        )

    def test_unreachable_002(self):
        """Report an issue if the URL is a relative path that doesn't point to something on-disk."""
        name = "some_package"
        code = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            help = "README.md"
            """
        )

        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package help has an un-reachable URL"
        ]

        self.assertEqual(1, len(issues))

    def test_unreachable_003(self):
        """Report an issue if the URL is an absolute path that doesn't point to something on-disk."""
        absolute_root = tempfile.mkdtemp()
        shutil.rmtree(absolute_root)

        name = "some_package"
        template = textwrap.dedent(
            """\
            name = "some_package"
            version = "1.0.0"
            help = "{absolute_root}"
            """
        )
        code = template.format(absolute_root=absolute_root)

        directory = packaging.make_fake_source_package(name, code)
        self.add_item(os.path.dirname(directory))

        results = cli.lint(directory)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package help has an un-reachable URL"
        ]

        self.assertEqual(1, len(issues))

    @mock.patch("python_compatibility.website.is_internet_on")
    def test_internet_down(self, is_internet_on):
        """Make sure this checker does not raise an exception if the user is offline."""
        is_internet_on.return_value = False
        self._test_not_found(
            "some_package",
            textwrap.dedent(
                """\
                name = "some_package"
                version = "1.0.0"
                help = "something_that_doesnt_exist.com"
                """
            ),
        )


def _get_rezbuild_text():
    """Create a basic rezbuild.py file's contents."""
    return textwrap.dedent(
        """\
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-

        # IMPORT STANDARD LIBRARIES
        import os
        import shutil
        import sys


        def build(source_path, install_path):
            for folder in {"python", }:
                source = os.path.join(source_path, folder)
                destination = os.path.join(install_path, folder)
                shutil.copytree(source, destination)

        if __name__ == "__main__":
            build(
                source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
                install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
            )
        """
    )
