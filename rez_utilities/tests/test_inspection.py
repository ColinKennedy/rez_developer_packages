#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test all functions in the :mod:`rez_utilities.inspection` module."""

import collections
import functools
import os
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
from rez import packages_, resolved_context
from rez.config import config
from rez_utilities import creator, inspection
from rezplugins.build_process import local

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def _has_versioned_parent_package_folder():
    """bool: Check if this unittest suite is being run from a built Rez package."""
    package = inspection.get_nearest_rez_package(_CURRENT_DIRECTORY)
    root = inspection.get_package_root(package)
    folder = os.path.basename(root)

    return folder == os.environ["REZ_{name}_VERSION".format(name=package.name.upper())]


class Packaging(common.Common):
    """Check that Rez package files are found correctly."""

    @unittest.skipIf(
        _has_versioned_parent_package_folder(),
        "This unittest is being run from a built package",
    )
    def test_built_package_false(self):
        """Check that source Rez packages do not return True for :func:`.is_built_package`."""
        package = inspection.get_nearest_rez_package(
            os.path.dirname(_CURRENT_DIRECTORY)
        )
        self.assertFalse(inspection.is_built_package(package))

    def test_built_package_invalid(self):
        """Check that non-package input to :func:`.is_built_package` raises an exception."""
        with self.assertRaises(ValueError):
            inspection.is_built_package(None)

    def test_detect_found_001(self):
        """Check that valid directory input can find Rez packages correctly."""
        self.assertIsNotNone(
            inspection.get_nearest_rez_package(os.path.dirname(_CURRENT_DIRECTORY))
        )

    def test_detect_found_002(self):
        """Check that valid directory input can find Rez packages correctly."""
        self.assertIsNotNone(inspection.get_nearest_rez_package(_CURRENT_DIRECTORY))

    def test_detect_found_003(self):
        """Check that valid directory input can find Rez packages correctly."""
        self.assertIsNotNone(
            inspection.get_nearest_rez_package(os.path.join(_CURRENT_DIRECTORY, "foo"))
        )

    def test_detect_missing(self):
        """Check that a directory that has no Rez package returns None."""
        directory = tempfile.mkdtemp(suffix="_detect_missing")
        self.delete_item_later(directory)

        self.assertIsNone(inspection.get_nearest_rez_package(directory))

    def test_in_valid_context(self):
        """Make sure :func:`rez_lint.inspection.in_valid_context` works as expected."""
        package = inspection.get_nearest_rez_package(_CURRENT_DIRECTORY)

        Package = collections.namedtuple("Package", "name version")
        fake_package = Package("foo", "6.6.6")

        self.assertTrue(inspection.in_valid_context(package))
        self.assertFalse(inspection.in_valid_context(fake_package))


class HasPythonPackage(common.Common):
    """Test that the :func:`rez_utilities.inspection.has_python_package` function works."""

    def setUp(self):
        """Keep a copy of the Rez build command so that unittests can mock it."""
        self._saved_build_method = local.LocalBuildProcess.build
        self._saved_in_valid_context = inspection.in_valid_context

    def tearDown(self):
        """Restore the old build command."""
        local.LocalBuildProcess.build = self._saved_build_method
        inspection.in_valid_context = self._saved_in_valid_context

    def test_source(self):
        """Return True if a Rez package with at least one Python module is found."""
        root = tempfile.mkdtemp(
            suffix="_a_rez_source_package_that_has_at_least_1_python_module"
        )
        self.delete_item_later(root)
        root = os.path.join(root, "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"
                    version = "1.0.0"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        python_root = os.path.join(root, "python", "some_package")
        os.makedirs(python_root)

        open(os.path.join(python_root, "__init__.py"), "a").close()
        open(os.path.join(python_root, "some_module.py"), "a").close()

        local.LocalBuildProcess.build = _check_called(local.LocalBuildProcess.build)

        package = inspection.get_nearest_rez_package(root)
        self.assertTrue(
            inspection.has_python_package(
                package,
                paths=[root] + config.packages_path,  # pylint: disable=no-member
                allow_build=False,
            )
        )

        self.assertFalse(local.LocalBuildProcess.build.was_run)

    def test_source_build(self):
        """Return True if a Rez package creates a Python module after build."""
        root = tempfile.mkdtemp(
            suffix="_a_rez_source_package_with_no_python_modules_until_build"
        )
        self.delete_item_later(root)
        root = os.path.join(root, "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"
                    version = "1.0.0"
                    build_command = "python {root}/rezbuild.py {install}"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        with open(os.path.join(root, "rezbuild.py"), "w") as handler:
            handler.write(_get_rezbuild_text())

        python_root = os.path.join(root, "python", "some_package")
        os.makedirs(python_root)

        open(os.path.join(python_root, "__init__.py"), "a").close()

        local.LocalBuildProcess.build = _check_called(local.LocalBuildProcess.build)

        package = inspection.get_nearest_rez_package(root)
        self.assertTrue(
            inspection.has_python_package(
                package,
                paths=[root] + config.packages_path,  # pylint: disable=no-member
                allow_build=True,
            )
        )

        self.assertTrue(local.LocalBuildProcess.build.was_run)

    def test_source_with_variants(self):
        """A Rez source package that contains a Python package should return true.

        If that source package has variants, as long as the variant contains
        a Python module, it shouldn't need to be built and still return True.

        """
        root = tempfile.mkdtemp(suffix="_a_rez_source_package_with_a_variant")
        self.delete_item_later(root)
        root = os.path.join(root, "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"
                    version = "1.0.0"
                    variants = [["python-2"]]

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        python_root = os.path.join(root, "python", "some_package")
        os.makedirs(python_root)

        open(os.path.join(python_root, "__init__.py"), "a").close()
        open(os.path.join(python_root, "some_module.py"), "a").close()

        local.LocalBuildProcess.build = _check_called(local.LocalBuildProcess.build)

        package = inspection.get_nearest_rez_package(root)
        self.assertTrue(
            inspection.has_python_package(
                package,
                paths=[root] + config.packages_path,  # pylint: disable=no-member
                allow_build=False,
            )
        )

        self.assertFalse(local.LocalBuildProcess.build.was_run)

    def test_build(self):
        """A build Rez package should return True if it has a Python module inside of it."""
        root = tempfile.mkdtemp(
            suffix="_a_rez_source_package_with_no_python_modules_until_build"
        )
        self.delete_item_later(root)
        root = os.path.join(root, "some_package")
        os.makedirs(root)

        with open(os.path.join(root, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    name = "some_package"
                    version = "1.0.0"
                    build_command = "python {root}/rezbuild.py {install}"

                    def commands():
                        import os

                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        with open(os.path.join(root, "rezbuild.py"), "w") as handler:
            handler.write(_get_rezbuild_text())

        python_root = os.path.join(root, "python", "some_package")
        os.makedirs(python_root)

        open(os.path.join(python_root, "__init__.py"), "a").close()

        package = inspection.get_nearest_rez_package(root)

        install_root = tempfile.mkdtemp(suffix="_installed_rez_package")
        self.delete_item_later(install_root)

        build_package = creator.build(package, install_root, quiet=True)

        self.assertTrue(
            inspection.has_python_package(
                build_package,
                paths=[root] + config.packages_path,  # pylint: disable=no-member
                allow_build=True,
            )
        )

    def test_python_package_true(self):
        """Make sure a source Rez package with no variant still works."""
        package = inspection.get_nearest_rez_package(
            os.path.dirname(_CURRENT_DIRECTORY)
        )
        self.assertTrue(inspection.has_python_package(package))

    def test_python_package_invalid(self):
        """Make sure a non-package input raises an exception."""
        with self.assertRaises(ValueError):
            inspection.has_python_package(None)

    def test_allow_current_context(self):
        """Check that has_python_package only creates a context when needed."""
        package = inspection.get_nearest_rez_package(_CURRENT_DIRECTORY)
        inspection.in_valid_context = _check_called(inspection.in_valid_context)

        self.assertTrue(
            inspection.has_python_package(package, allow_current_context=False)
        )
        self.assertFalse(inspection.in_valid_context.was_run)
        self.assertTrue(
            inspection.has_python_package(package, allow_current_context=True)
        )
        self.assertTrue(inspection.in_valid_context.was_run)


class GetPackagePythonFiles(common.Common):
    """Check that the :func:`rez_utilities.inspection.get_package_python_paths` works."""

    def _make_fake_rez_install_package(self, name, version, text):
        """Create an installed (built) Rez package.

        Note:
            This method creates Python files whether `text` actually
            appends to PYTHONPATH or not. They just get ignored by
            unittests, in that case.

        Args:
            name (str):
                The name of the Rez package family to make.
            version (str):
                The major, minor, and patch information for the package.
                e.g. "1.0.0".
            text (str):
                The source code used for the package.py file.

        Returns:
            :class:`rez.developer_package.DeveloperPackage`: The created instance.

        """
        root = tempfile.mkdtemp(suffix="_rez_install_package_get_package_python_paths")
        directory = os.path.join(root, name, version)
        self.delete_item_later(root)

        python_root = os.path.join(directory, "python")
        os.makedirs(python_root)

        open(os.path.join(python_root, "thing.py"), "w").close()
        open(os.path.join(python_root, "another.py"), "w").close()

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(text)

        return packages_.get_developer_package(directory), root

    def _make_fake_rez_source_package(self, name, text):
        """Create a source (non-installed) Rez package.

        Args:
            name (str): The name of the Rez package family to make.
            text (str): The source code used for the package.py file.

        Returns:
            :class:`rez.developer_package.DeveloperPackage`: The created instance.

        """
        root = tempfile.mkdtemp(suffix="_rez_source_package_get_package_python_paths")
        directory = os.path.join(root, name)
        os.makedirs(directory)
        self.delete_item_later(root)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(text)

        return packages_.get_developer_package(directory)

    def _make_test_case(self, name, text, extra_paths=None):
        """Create a Rez package that has some Python files inside of it.

        This method exists to make unittesting a bit easier to understand.

        Note:
            This method creates Python files whether `text` actually
            appends to PYTHONPATH or not. They just get ignored by
            unittests, in that case.

        Args:
            name (str):
                The name of the Rez package family to make.
            text (str):
                The source code used for the package.py file.
            extra_paths (list[str], optional):
                A list of paths used to search for Rez packages
                during the Rez resolve that this function calls.
                If no paths are given, Rez will default to
                :attr:`rez.config.packages_path` instead. Default is
                None.

        Returns:
            tuple[set[str], str]:
                The found Python files (excluding __init__.py files)
                and the parent folder where the created package.py goes.

        """
        if not extra_paths:
            extra_paths = []

        package = self._make_fake_rez_source_package(name, text)
        root = inspection.get_package_root(package)
        python_root = os.path.join(root, "python")
        os.makedirs(python_root)

        open(os.path.join(python_root, "thing.py"), "w").close()
        open(os.path.join(python_root, "another.py"), "w").close()

        context = resolved_context.ResolvedContext(
            ["{package.name}==".format(package=package)],
            package_paths=[inspection.get_packages_path_from_package(package)]
            + extra_paths
            + config.packages_path,  # pylint: disable=no-member
        )

        paths = inspection.get_package_python_paths(
            package, context.get_environ().get("PYTHONPATH", "").split(os.pathsep)
        )

        return paths, root

    def _make_test_dependencies(self):
        """Create a couple of generic, installed Rez packages to use for unittesting."""
        # To actually make this test work, "some_fake_package" needs some variants.
        #
        # It may be overkill, but we're going to make some quick Rez packages
        # that can be used for variants.
        #
        dependency1, _ = self._make_fake_rez_install_package(
            "some_dependency",
            "1.1.0",
            textwrap.dedent(
                """\
                name = "some_dependency"
                version = "1.1.0"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            ),
        )

        dependency2, _ = self._make_fake_rez_install_package(
            "another_one",
            "2.3.0",
            textwrap.dedent(
                """\
                name = "another_one"
                version = "2.3.0"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            ),
        )

        return [
            inspection.get_packages_path_from_package(dependency1),
            inspection.get_packages_path_from_package(dependency2),
        ]

    def test_empty(self):
        """Return nothing because the package does not modify the PYTHONPATH."""
        python_files, _ = self._make_test_case(
            "some_fake_package",
            textwrap.dedent(
                """\
                name = "some_fake_package"
                version = "1.0.0"

                def commands():
                    pass
                """
            ),
        )

        self.assertEqual(set(), python_files)

    def test_undefined(self):
        """Return nothing because the package does not modify the PYTHONPATH."""
        python_files, _ = self._make_test_case(
            "some_fake_package",
            textwrap.dedent(
                """\
                name = "some_fake_package"
                version = "1.0.0"
                """
            ),
        )

        self.assertEqual(set(), python_files)

    def test_source_package_no_variants(self):
        """Create a source Rez package with no variants and get the PYTHONPATH folders."""
        python_files, root = self._make_test_case(
            "some_fake_package",
            textwrap.dedent(
                """\
                name = "some_fake_package"
                version = "1.0.0"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            ),
        )

        self.assertEqual({os.path.join(root, "python")}, python_files)

    def test_source_package_with_variants(self):
        """Create a source Rez package with variants and get the folders affecting PYTHONPATH."""
        dependencies = self._make_test_dependencies()
        python_files, root = self._make_test_case(
            "some_fake_package",
            textwrap.dedent(
                """\
                name = "some_fake_package"
                version = "1.0.0"
                variants = [["some_dependency-1", "another_one-2.3"], ["another_one-2.3"]]

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            ),
            extra_paths=dependencies,
        )

        self.assertEqual({os.path.join(root, "python")}, python_files)

    def test_installed_package_no_variants(self):
        """Create a Rez package with no variants and get the folders affecting PYTHONPATH."""
        dependencies = self._make_test_dependencies()
        package, root = self._make_fake_rez_install_package(
            "some_fake_package",
            "1.0.0",
            textwrap.dedent(
                """\
                name = "some_fake_package"
                version = "1.0.0"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            ),
        )

        context = resolved_context.ResolvedContext(
            ["{package.name}==1.0.0".format(package=package)],
            package_paths=[inspection.get_packages_path_from_package(package)]
            + dependencies
            + config.packages_path,  # pylint: disable=no-member
        )

        python_files = inspection.get_package_python_paths(
            package, context.get_environ().get("PYTHONPATH", "").split(os.pathsep)
        )

        self.assertEqual(
            {os.path.join(root, "some_fake_package", "1.0.0", "python")}, python_files
        )

    def test_installed_package_with_variants(self):
        """Create a Rez package with variants and get the folders affecting PYTHONPATH."""
        dependencies = self._make_test_dependencies()
        package = self._make_fake_rez_source_package(
            "some_fake_package",
            textwrap.dedent(
                """\
                name = "some_fake_package"
                version = "1.0.0"
                variants = [["some_dependency-1", "another_one-2.3"], ["another_one-2.3"]]
                build_command = "echo 'foo'"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            ),
        )
        install_path = tempfile.mkdtemp(suffix="_install_path")
        self.delete_item_later(install_path)

        build_package = creator.build(
            package,
            install_path,
            packages_path=dependencies
            + config.packages_path,  # pylint: disable=no-member
            quiet=True,
        )

        context = resolved_context.ResolvedContext(
            ["{build_package.name}==1.0.0".format(build_package=build_package)],
            package_paths=[inspection.get_packages_path_from_package(build_package)]
            + dependencies
            + config.packages_path,  # pylint: disable=no-member
        )

        python_files = inspection.get_package_python_paths(
            build_package, context.get_environ().get("PYTHONPATH", "").split(os.pathsep)
        )

        self.assertEqual(
            {
                os.path.join(
                    install_path,
                    "some_fake_package",
                    "1.0.0",
                    "another_one-2.3",
                    "python",
                )
            },
            python_files,
        )


def _check_called(function):
    """Add an extra attribute to a given function to track if Python has called it."""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """Add the `was_run` attribute to this function call."""
        try:
            result = function(*args, **kwargs)
        except Exception:
            raise
        finally:
            wrapper.was_run = True

        return result

    wrapper.was_run = False

    return wrapper


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

            open(
                os.path.join(install_path, "python", "some_package", "some_module.py"),
                "a",
            ).close()

        if __name__ == "__main__":
            build(
                source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
                install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
            )
        """
    )
