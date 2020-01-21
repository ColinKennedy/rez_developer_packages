#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test all of the checkers in "dangers.py"."""

import os
import tempfile
import textwrap

from rez import packages_
from rez.config import config
from rez_lint import cli
from rez_utilities import creator, inspection

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
        config.packages_path[:] = [
            directory,
            dependency_path,
        ] + original  # pylint: disable=no-member

        try:
            results = cli.lint(directory)
        except Exception:
            raise
        finally:
            config.packages_path[:] = original  # pylint: disable=no-member

        has_issue = any(
            description
            for description in results
            if description.get_summary()[0]
            == "Improper package requirements were found"
        )

        self.assertFalse(has_issue)

    # TODO : Do these
    # def test_one_improper(self):
    #     pass
    #
    # def test_multiple_impropers(self):
    #     pass
    #
    # def test_mixed_impropers(self):
    #     pass


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

        original = list(config.packages_path)
        config.packages_path = [dependency1_build_path] + config.packages_path

        try:
            creator.build(
                packages_.get_developer_package(dependency2_directory),
                dependency2_build_path,
            )
        finally:
            config.packages_path[:] = original

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
    """Test that the :class:`rez_lint.plugins.checkers.dangers.RequirementsNotSorted.` class works."""

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
        ))
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
        ))
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
        ))
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
            if description.get_summary()[0] == "Package has too many dependencies (0/10)"
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

        results = cli.lint(root)

        issues = [
            description
            for description in results
            if description.get_summary()[0] == "Package has too many dependencies (11/10)"
        ]

        self.assertEqual(1, len(issues))


# class UrlNotReachable(unittest.TestCase):
#     def test_undefined(self):
#         pass
#
#     def test_empty(self):
#         pass
#
#     def test_reachable_001(self):
#         pass
#
#     def test_reachable_002(self):
#         """Test that having a single ``help`` URL is allowed, as long it's reachable."""
#         pass
#
#     def test_unreachable(self):
#         pass
#
#     def test_internet_down(self):
#         """Make sure this checker does not raise an exception if the user is offline."""
#         pass


def _get_rezbuild_text():
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
