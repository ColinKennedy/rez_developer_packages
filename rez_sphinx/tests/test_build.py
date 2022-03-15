"""Make sure :doc:`build_command` works as expected."""

import os
import stat
import tempfile
import textwrap
import unittest

from python_compatibility import wrapping
from rez import exceptions as exceptions_
from rez import resolved_context
from rez.config import config as config_
from rez_utilities import creator, finder

from rez_sphinx.core import bootstrap, exception, sphinx_helper

from .common import package_wrap, pypi_check, run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_PYPI_RTD = "sphinx-rtd-theme==1.0.0"


class ApiDocOptions(unittest.TestCase):
    """Make sure users can source options from the CLI / rez-config / etc."""

    def test_cli_argument(self):
        """Let the user change :ref:`sphinx-quickstart` options from a flag."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_cli_argument")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing():  # Make tests less spammy
                run_test.test(
                    'build "{source_directory}" '
                    '--apidoc-arguments "--suffix .txt"'.format(
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
        install_path = package_wrap.make_directory("_test_cli_dash_separator")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing():  # Make tests less spammy
                run_test.test(["build", source_directory, "--", "--suffix", ".txt"])

        source = os.path.join(source_directory, "documentation", "source")

        self.assertEqual(
            {".gitignore", "some_package.txt", "some_package.file.txt", "modules.txt"},
            set(os.listdir(os.path.join(source, "api"))),
        )


class Bootstrap(unittest.TestCase):
    """Make sure :func:`rez_sphinx.core.bootstrap.bootstrap` works."""

    def _quick_ignore_test(self, text):
        """Check ``text`` does not find add any intersphinx candidates.

        Args:
            text (str):
                Extra Python code to append to the test Rez package. e.g.
                ``'requires = ["!excluded_package"]'``.

        """
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
    """Make sure :doc:`build_command` works as expected."""

    def _hello_world_test(self):
        """Create a basic :ref:`rez_sphinx` "init + build"."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_Build_hello_world_test")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing():  # Make tests less spammy
                run_test.test(["build", source_directory])

        source = os.path.join(source_directory, "documentation", "source")
        api_directory = os.path.join(source, "api")
        source_master = os.path.join(source, "index.rst")

        with open(source_master, "r") as handler:
            data = handler.read()

        master_toctrees = [
            "\n".join(tree) for _, _, tree in sphinx_helper.get_toctrees(data)
        ]
        build = os.path.join(source_directory, "documentation", "build")

        self.assertEqual(
            {
                ".gitignore",
                "README",
                "modules.rst",
                "some_package.file.rst",
                "some_package.rst",
            },
            set(os.listdir(api_directory)),
        )

        self.assertEqual(1, len(master_toctrees))
        self.assertEqual(
            textwrap.dedent(
                """\
                .. toctree::
                   :maxdepth: 2
                   :caption: Contents:

                   developer_documentation
                   user_documentation
                   API Documentation <api/modules>"""
            ),
            master_toctrees[0],
        )
        self.assertTrue(os.path.isfile(os.path.join(api_directory, ".gitignore")))
        self.assertTrue(os.path.isfile(os.path.join(build, "index.html")))
        self.assertTrue(
            os.path.isfile(os.path.join(build, "api", "some_package.file.html"))
        )

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
                ) as watcher, wrapping.silence_printing():  # Make tests less spammy
                    run_test.test(["build", source])

                watchers.extend(watcher)

        raise ValueError("sTop")

        for watcher in watchers:
            print("result", watcher.get_all_results())


class ExtraRequires(unittest.TestCase):
    """Make sure :ref:`rez_sphinx's <rez_sphinx>` "extra_requires" works."""

    def test_normal(self):
        """Allow users to pass extra :ref:`requires` to :ref:`rez_sphinx`."""
        extra_install_path = os.path.join(
            _CURRENT_DIRECTORY, "data", "installed_packages"
        )
        context = _make_current_rez_sphinx_context(
            package_paths=config_.packages_path + [extra_install_path]
        )
        expected_requires = ["something-2"]
        resolved_nothing = context.get_resolved_package("something")

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["extra_requires"] = expected_requires

            context = _make_current_rez_sphinx_context(
                package_paths=config.packages_path + [extra_install_path]
            )

            resolved_something = context.get_resolved_package("something")

        self.assertIsNone(resolved_nothing)
        self.assertIsNotNone(resolved_something)

    def test_package_conflict(self):
        """Prevent using :ref:`rez_sphinx` if "extra_requires" is invalid."""
        conflict = ["python-1"]

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["extra_requires"] = conflict

            with self.assertRaises(exceptions_.ResolveError):
                _make_current_rez_sphinx_context(package_paths=config.packages_path)


class Miscellaneous(unittest.TestCase):
    """Any test that doesn't make sense in other places."""

    @unittest.skipIf(
        not pypi_check.is_request_installed(_PYPI_RTD),
        "Install sphinx-rtd-theme with `rez-pip --install {_PYPI_RTD} --python-version=3`".format(
            _PYPI_RTD=_PYPI_RTD,
        ),
    )
    def test_sphinx_rtd_theme(self):
        """Ensure it's easy to install :ref:`sphinx-rtd-theme`."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_api_pass_cli")

        creator.build(source_package, install_path, quiet=True)

        with wrapping.keep_cwd(), run_test.keep_config() as config:
            # Simulate the user adding sphinx-rtd-theme as a requirement and
            # then running rez_sphinx init / build.
            #
            # (Technically we only need the requirement :doc:`build_command`
            # but it can't hurt to run it both init + build)
            #
            optionvars = {
                "rez_sphinx": {
                    "extra_requires": [pypi_check.to_rez_request(_PYPI_RTD)],
                    "sphinx_conf_overrides": {
                        "html_theme": "sphinx_rtd_theme",
                    },
                },
            }
            config.optionvars = optionvars
            # Simulate the user making a "rez_sphinx + current Rez package environment"
            os.chdir(source_directory)

            context = _make_current_rez_sphinx_context(
                extra_request=[
                    "{source_package.name}=={source_package.version}".format(
                        source_package=source_package
                    ),
                ],
                package_paths=config_.packages_path + [install_path],
            )

            # Now simulate rez_sphinx init + build
            quick_configuration = _make_rez_configuration(
                "optionvars = {optionvars!r}".format(optionvars=optionvars)
            )
            parent_environment = {"REZ_CONFIG_FILE": quick_configuration}

            init = context.execute_command(
                "rez_sphinx init",
                parent_environ=parent_environment,
            )
            init.communicate()
            build = context.execute_command(
                "rez_sphinx build",
                parent_environ=parent_environment,
            )
            build.communicate()
            self.assertEqual(0, init.returncode)
            self.assertEqual(0, build.returncode)

        with open(
            os.path.join(source_directory, "documentation", "build", "index.html"), "r"
        ) as handler:
            contents = handler.read()

        self.assertIn("Read the Docs", contents)


class Options(unittest.TestCase):
    """Make sure options (CLI, rez-config, etc) work as expected."""

    def test_api_pass_cli(self):
        """Don't auto-build API documentation because the CLI said not to."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_api_pass_cli")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])
            run_test.test(["build", source_directory, "--no-apidoc"])

        source = os.path.join(source_directory, "documentation", "source")
        api_directory = os.path.join(source, "api")

        self.assertFalse(os.path.isdir(api_directory))

    def test_api_pass_config(self):
        """Don't auto-build API documentation because the config said not to."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_api_pass_config")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with run_test.keep_config() as config:
                config.optionvars["rez_sphinx"] = dict()
                config.optionvars["rez_sphinx"]["enable_apidoc"] = False

                run_test.test(["build", source_directory])

        source = os.path.join(source_directory, "documentation", "source")
        api_directory = os.path.join(source, "api")

        self.assertFalse(os.path.isdir(api_directory))


class Invalid(unittest.TestCase):
    """Make sure :doc:`build_command` fails when expected."""

    def test_apidoc_argument_conflict(self):
        """If the user specifies --apidoc-arguments and --no-apidoc at once."""
        directory = package_wrap.make_directory("_test_apidoc_argument_conflict")

        with self.assertRaises(exception.UserInputError):
            run_test.test(
                ["build", directory, "--no-apidoc", "--apidoc-arguments", "blah"]
            )

    def test_bad_permissions(self):
        """Fail building if the user lacks permissions to write to-disk."""
        directory = package_wrap.make_directory(
            "_test_build_Invalid_test_bad_permissions"
        )

        _make_read_only(directory)

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
        directory = package_wrap.make_directory("_test_auto_api_no_python_files")

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

        install_directory = package_wrap.make_directory(
            "_test_auto_api_no_python_files_install_root"
        )
        install_package_root = os.path.join(install_directory, "foo", "1.0.0")
        os.makedirs(install_package_root)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(template)

        with open(os.path.join(install_package_root, "package.py"), "w") as handler:
            handler.write(template)

        with self.assertRaises(exception.NoPythonFiles), wrapping.keep_os_environment():
            os.environ["REZ_FOO_ROOT"] = install_package_root

            run_test.test(["build", directory])


def _make_current_rez_sphinx_context(extra_request=tuple(), package_paths=tuple()):
    """:class:`rez.resolved_context.ResolvedContext`: Get the context for :ref:`rez_sphinx`."""
    extra_request = extra_request or list(extra_request)
    package = finder.get_nearest_rez_package(_CURRENT_DIRECTORY)
    request = ["{package.name}=={package.version}".format(package=package)]

    return resolved_context.ResolvedContext(
        request + extra_request, package_paths=package_paths
    )


def _make_read_only(path):
    """Change ``path`` to not allow writing.

    Reference:
        https://stackoverflow.com/a/51262451/3626104

    Args:
        path (str): The absolute or relative path to a file or directory on-disk.

    """
    mode = os.stat(path).st_mode
    read_only_mask = 0o777 ^ (stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
    os.chmod(path, mode & read_only_mask)


def _make_rez_configuration(text):
    """str: Create a rezconfig.py, using ``text``."""
    directory = package_wrap.make_directory("_make_rez_configuration")
    configuration = os.path.join(directory, "rezconfig.py")

    with open(configuration, "w") as handler:
        handler.write(text)

    return configuration
