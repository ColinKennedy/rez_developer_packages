#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test all functions in the :mod:`rez_utilities.inspection` module."""


import functools
import os
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
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
        directory = tempfile.mkdtemp()
        self.add_item(directory)

        self.assertIsNone(inspection.get_nearest_rez_package(directory))


class HasPythonPackage(common.Common):
    """Test that the :func:`rez_utilities.inspection.has_python_package` function works."""

    def setUp(self):
        """Keep a copy of the Rez build command so that unittests can mock it."""
        self._saved_build_method = local.LocalBuildProcess.build

    def tearDown(self):
        """Restore the old build command."""
        local.LocalBuildProcess.build = self._saved_build_method

    def test_source(self):
        """Return True if a Rez package with at least one Python module is found."""
        root = tempfile.mkdtemp(
            suffix="_a_rez_source_package_that_has_at_least_1_python_module"
        )
        self.add_item(root)
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
        self.add_item(root)
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
            handler.write(
                textwrap.dedent(
                    '''\
                    #!/usr/bin/env python
                    # -*- coding: utf-8 -*-

                    """The main module which installs Maya onto the user's system."""

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
                    '''
                )
            )

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
        root = tempfile.mkdtemp(
            suffix="_a_rez_source_package_with_a_variant"
        )
        self.add_item(root)
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
        self.add_item(root)
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
            handler.write(
                textwrap.dedent(
                    '''\
                    #!/usr/bin/env python
                    # -*- coding: utf-8 -*-

                    """The main module which installs Maya onto the user's system."""

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
                    '''
                )
            )

        python_root = os.path.join(root, "python", "some_package")
        os.makedirs(python_root)

        open(os.path.join(python_root, "__init__.py"), "a").close()

        package = inspection.get_nearest_rez_package(root)

        install_root = tempfile.mkdtemp(suffix="_installed_rez_package")
        self.add_item(install_root)

        build_package = creator.build(package, install_root)

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


def _check_called(function):
    """Add an extra attribute to a given function to track if Python has called it."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        except Exception:
            raise
        finally:
            wrapper.was_run = True

        return result

    wrapper.was_run = False

    return wrapper
