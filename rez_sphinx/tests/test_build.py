"""Make sure :ref:`rez_sphinx build` works as expected."""

import os
import unittest
import textwrap
import tempfile

from python_compatibility import wrapping
from rez_sphinx.core import bootstrap, sphinx_helper, exception
from rez_utilities import creator, finder

from .common import package_wrap, run_test


class ApiDocOptions(unittest.TestCase):
    """Make sure users can source options from the CLI / rez-config / etc."""

    def test_cli_argument(self):
        """Let the user change :ref:`sphinx-quickstart` options from a flag."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("Build_test_cli_argument")
        installed_package = creator.build(source_package, install_path)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])
            run_test.test(
                'build "{source_directory}" --apidoc-arguments "--suffix .txt"'.format(
                    source_directory=source_directory
                )
            )

        source = os.path.join(source_directory, "documentation", "source")

        self.assertEqual(
            {".gitignore", "some_package.txt", "some_package.file.txt", "modules.txt"},
            set(os.listdir(os.path.join(source, "api"))),
        )

    def test_cli_dash_separator(self):
        """Let the user change :ref:`sphinx-quickstart` options from a " -- "."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("Build_test_cli_dash_argument")
        installed_package = creator.build(source_package, install_path)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])
            run_test.test(["build", source_directory, "--", "--suffix", ".txt"])

        source = os.path.join(source_directory, "documentation", "source")

        self.assertEqual(
            {".gitignore", "some_package.txt", "some_package.file.txt", "modules.txt"},
            set(os.listdir(os.path.join(source, "api"))),
        )


class Bootstrap(unittest.TestCase):
    """Make sure :func:`rez_sphinx.core.bootstrap.bootstrap` works."""

    def _quick_ignore_test(self, text):
        """Unittest that including ``text`` does not get add any intersphinx candidates."""
        directory = package_wrap.make_directory("_quick_ignore_test")

        template = textwrap.dedent(
            """\
            name = "foo"

            version = "1.0.0"
            """
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(template + "\n\n" + text)

        package = finder.get_nearest_rez_package(directory)

        with wrapping.watch_namespace(
            bootstrap._get_intersphinx_candidates
        ) as watchers:
            bootstrap.bootstrap(dict(), package=package)

        for watcher in watchers:
            self.assertEqual(set(), watcher.get_all_results())

    def test_intersphinx_allow_weak(self):
        """Allow weak packages if they are part of the resolve."""
        raise ValueError()

    def test_intersphinx_ignore_conflict(self):
        """Don't consider excluded packages."""
        self._quick_ignore_test('requires = ["!excluded_package"]')

    def test_intersphinx_ignore_ephemeral(self):
        """Don't consider ephemeral packages."""
        self._quick_ignore_test('variants = [[".some_ephemeral-1"]]')

    def test_intersphinx_ignore_weak(self):
        """Don't consider weak packages which aren't part of the resolve."""
        self._quick_ignore_test('requires = ["~some_not_requested_package"]')


class Build(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build` works as expected."""

    def _hello_world_test(self):
        """Create a basic :ref:`rez_sphinx` "init + build"."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory(
            "Build_test_hello_world_install_root"
        )
        installed_package = creator.build(source_package, install_path)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])
            run_test.test(["build", source_directory])

        source = os.path.join(source_directory, "documentation", "source")
        api_directory = os.path.join(source, "api")
        api_source_gitignore = os.path.join(api_directory, ".gitignore")
        source_master = os.path.join(source, "index.rst")

        with open(source_master, "r") as handler:
            data = handler.read()

        master_toctrees = [
            "\n".join(tree) for _, _, tree in sphinx_helper.get_toctrees(data)
        ]
        build = os.path.join(source_directory, "documentation", "build")
        build_master = os.path.join(build, "index.html")
        example_api_path = os.path.join(build, "api", "some_package.file.html")

        self.assertEqual(
            {".gitignore", "modules.rst", "some_package.file.rst", "some_package.rst"},
            set(os.listdir(api_directory)),
        )

        self.assertEqual(1, len(master_toctrees))
        self.assertEqual(
            textwrap.dedent(
                """\
                .. toctree::
                   :maxdepth: 2
                   :caption: Contents:

                   API Documentation <api/modules>"""
            ),
            master_toctrees[0],
        )
        self.assertTrue(os.path.isfile(api_source_gitignore))
        self.assertTrue(os.path.isfile(build_master))
        self.assertTrue(os.path.isfile(example_api_path))

    def test_hello_world(self):
        """Build documentation and auto-API .rst documentation onto disk."""
        self._hello_world_test()

    def test_hello_world_other_folder(self):
        """Build documentation again, but from a different PWD."""
        with wrapping.keep_cwd():
            os.chdir(tempfile.gettempdir())
            self._hello_world_test()

    def test_intersphinx_loading(self):
        """Make sure sphinx.ext.intersphinx "sees" Rez packages as expected."""
        package_directories = package_wrap.make_dependent_packages()
        install_packages = [install for _, install in package_directories]
        watchers = []

        for source, install in package_directories:
            with run_test.simulate_resolve(install_packages):
                run_test.test(["init", source])

                with wrapping.watch_namespace(
                    bootstrap._get_intersphinx_mappings
                ) as watcher:
                    run_test.test(["build", source])

                watchers.extend(watcher)

        for watcher in watchers:
            print("result", watcher.get_all_results())


class Options(unittest.TestCase):
    """Make sure options (CLI, rez-config, etc) work as expected."""

    def test_auto_api_config(self):
        """Build API documentation because the rez-config says to."""
        raise ValueError()

    def test_auto_api_explicit(self):
        """Build API documentation because the CLI flag was explicitly added."""
        raise ValueError()

    def test_auto_api_implicit(self):
        """Auto-build API documentation if no CLI flag or Rez config option is set."""
        raise ValueError()

    def test_auto_api_implicit_pass(self):
        """Don't auto-build API documentation if no CLI / config / auto-detect.

        If all systems fail, just warn the user in a log and build
        documentation as normal. It would just mean that the user didn't want
        to have auto-documentation.

        """
        raise ValueError()

    def test_generate_api_config(self):
        """Build API documentation because the rez-config says to."""
        raise ValueError()

    def test_generate_api_explicit(self):
        """Build API documentation because the CLI flag was explicitly added."""
        raise ValueError()

    def test_generate_api_implicit(self):
        """Auto-build API documentation if no CLI flag or Rez config option is set."""
        raise ValueError()

    def test_generate_api_implicit_pass(self):
        """Don't auto-build API documentation if no CLI / config / auto-detect.

        If all systems fail, just warn the user in a log and build
        documentation as normal. It would just mean that the user didn't want
        to have auto-documentation.

        """
        raise ValueError()


class Invalid(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build` fails when expected."""

    def test_bad_permissions(self):
        """Fail building if the user lacks permissions to write to-disk."""
        directory = package_wrap.make_directory("_test_build_Invalid_test_no_package")

        raise ValueError("Make read-only")

        with self.assertRaises(exception.NoPackageFound):
            run_test.test(["build", directory])

    def test_no_package(self):
        """Fail early if no Rez package was found."""
        directory = package_wrap.make_directory("_test_build_Invalid_test_no_package")

        with self.assertRaises(exception.NoPackageFound):
            run_test.test(["build", directory])

    def test_no_source(self):
        """Fail early if documentation source does not exist."""
        directory = package_wrap.make_directory("_test_no_source")

        template = textwrap.dedent(
            """\
            name = "foo"

            version = "1.0.0"
            """
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(template)

        with self.assertRaises(exception.NoDocumentationFound):
            run_test.test(["build", directory])

    def test_auto_api_no_python_files(self):
        """Fail to auto-build API .rst files if there's no Python files."""
        directory = package_wrap.make_directory("_test_no_source_source_root")

        template = textwrap.dedent(
            """\
            name = "foo"

            version = "1.0.0"
            """
        )

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(template)

        documentation_root = os.path.join(directory, "documentation", "source")
        os.makedirs(documentation_root)
        open(os.path.join(documentation_root, "conf.py"), "a").close()

        with open(os.path.join(documentation_root, "index.rst"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    .. toctree::
                       :maxdepth: 2
                       :caption: Contents:
                    """
                )
            )

        install_directory = package_wrap.make_directory("_test_no_source_install_root")
        install_package_root = os.path.join(install_directory, "foo", "1.0.0")
        os.makedirs(install_package_root)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(template)

        with open(os.path.join(install_package_root, "package.py"), "w") as handler:
            handler.write(template)

        with self.assertRaises(exception.NoPythonFiles), wrapping.keep_os_environment():
            os.environ["REZ_FOO_ROOT"] = install_package_root

            run_test.test(["build", directory])
