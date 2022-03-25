"""Make sure :ref:`rez_sphinx build` works as expected."""

import contextlib
import functools
import glob
import os
import shutil
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

from .common import doc_test, package_wrap, pypi_check, run_test

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_PACKAGE_ROOT = os.path.dirname(_CURRENT_DIRECTORY)
_PYPI_RTD = "sphinx-rtd-theme==1.0.0"


class ApiDocOptions(unittest.TestCase):
    """Make sure users can source options from the CLI / rez-config / etc."""

    def test_cli_argument(self):
        """Let the user change `sphinx-quickstart`_ options from a flag."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_cli_argument")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing(), run_test.allow_defaults():
                run_test.test(
                    'build run "{source_directory}" '
                    '--apidoc-arguments "--suffix .txt"'.format(
                        source_directory=source_directory
                    )
                )

        source = os.path.join(source_directory, "documentation", "source")

        self.assertEqual(
            {
                ".gitignore",
                "README",
                "modules.txt",
                "some_package.file.txt",
                "some_package.txt",
            },
            set(os.listdir(os.path.join(source, "api"))),
        )

    def test_cli_dash_separator(self):
        """Let the user change `sphinx-quickstart`_ options from a " -- "."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_cli_dash_separator")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing(), run_test.allow_defaults():
                run_test.test(
                    ["build", "run", source_directory, "--", "--suffix", ".txt"]
                )

        source = os.path.join(source_directory, "documentation", "source")

        self.assertEqual(
            {
                ".gitignore",
                "README",
                "modules.txt",
                "some_package.file.txt",
                "some_package.txt",
            },
            set(os.listdir(os.path.join(source, "api"))),
        )


class BootstrapIntersphinx(unittest.TestCase):
    """Make sure :func:`rez_sphinx.core.bootstrap.bootstrap` gets `intersphinx_mapping`_."""

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

    def test_allow_weak(self):
        """Allow weak packages if they are part of the resolve."""
        root = os.path.join(
            _PACKAGE_ROOT,
            "_test_data",
            "intersphinx_allow_weak",
        )
        source_root = os.path.join(root, "source_packages")
        install_root = os.path.join(root, "installed_packages")

        installed_packages = [
            finder.get_nearest_rez_package(path)
            for path in glob.glob(os.path.join(install_root, "*", "*"))
        ]
        name = "package_to_test"
        source_directory = os.path.join(source_root, name)

        with wrapping.silence_printing(), run_test.simulate_resolve(installed_packages):
            with _watch_candidates() as container, run_test.allow_defaults():
                run_test.test(["build", "run", source_directory])

        watcher = container[-1]
        _, _, results = watcher
        self.assertIn("weak_package", results)

    def test_fallback_package_links(self):
        """A package without documentation is find-able if it has a fallback path."""
        root = os.path.join(
            _PACKAGE_ROOT,
            "_test_data",
            "intersphinx_allow_weak",
        )
        source_root = os.path.join(root, "source_packages")
        install_root = os.path.join(root, "installed_packages")

        installed_packages = [
            finder.get_nearest_rez_package(path)
            for path in glob.glob(os.path.join(install_root, "*", "*"))
        ]
        name = "package_to_test"
        source_directory = os.path.join(source_root, name)

        fallback_map = {
            "weak_package": "foo",
        }

        # with wrapping.silence_printing(), run_test.simulate_resolve(installed_packages):
        with run_test.simulate_resolve(installed_packages):
            with _watch_intersphinx_mapping() as container, run_test.allow_defaults(), run_test.keep_config() as config:
                config.optionvars.setdefault("rez_sphinx", dict())
                config.optionvars["rez_sphinx"]["intersphinx_settings"] = dict()
                config.optionvars["rez_sphinx"]["intersphinx_settings"]["package_link_map"] = fallback_map

                run_test.test(["build", "run", source_directory])

        watcher = container[0]
        _, _, results = watcher

        expected = {
            # This comes directly from ``source_directory/documentation/source/conf.py``
            "https://docs.python.org/3/": None,
        }
        expected.update(fallback_map)
        self.assertEqual(expected, results)

    def test_ignore_conflict(self):
        """Don't consider excluded packages."""
        self._quick_ignore_test('requires = ["!excluded_package"]')

    def test_ignore_ephemeral(self):
        """Don't consider ephemeral packages."""
        self._quick_ignore_test('variants = [[".some_ephemeral-1"]]')

    def test_ignore_weak(self):
        """Don't consider weak packages which aren't part of the resolve."""
        self._quick_ignore_test('requires = ["~some_not_requested_package"]')


class ExtraRequires(unittest.TestCase):
    """Make sure :ref:`rez_sphinx's <rez_sphinx>` "extra_requires" works."""

    def test_normal(self):
        """Allow users to pass extra `requires`_ to :ref:`rez_sphinx`."""
        extra_install_path = os.path.join(
            _PACKAGE_ROOT, "_test_data", "resolve_requires", "installed_packages"
        )
        context = _make_current_rez_sphinx_context(
            package_paths=config_.packages_path + [extra_install_path]
        )
        expected_requires = ["pure_dependency-1"]
        resolved_nothing = context.get_resolved_package("pure_dependency")

        with run_test.keep_config() as config:
            config.optionvars["rez_sphinx"] = dict()
            config.optionvars["rez_sphinx"]["extra_requires"] = expected_requires

            context = _make_current_rez_sphinx_context(
                package_paths=config.packages_path + [extra_install_path]
            )

            resolved_something = context.get_resolved_package("pure_dependency")

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


class Invalid(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build run` fails when expected."""

    def test_apidoc_argument_conflict(self):
        """If the user specifies --apidoc-arguments and --no-apidoc at once."""
        directory = package_wrap.make_directory("_test_apidoc_argument_conflict")

        with self.assertRaises(exception.UserInputError), wrapping.silence_printing():
            run_test.test(
                ["build", "run", directory, "--no-apidoc", "--apidoc-arguments", "blah"]
            )

    def test_bad_permissions(self):
        """Fail building if the user lacks permissions to write to-disk."""
        directory = package_wrap.make_directory(
            "_test_build_Invalid_test_bad_permissions"
        )

        _make_read_only(directory)

        with self.assertRaises(exception.NoPackageFound), wrapping.silence_printing():
            run_test.test(["build", "run", directory])

    def test_no_package(self):
        """Fail early if no Rez package was found."""
        directory = package_wrap.make_directory("_test_build_Invalid_test_no_package")

        with self.assertRaises(exception.NoPackageFound), wrapping.silence_printing():
            run_test.test(["build", "run", directory])

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

        with self.assertRaises(
            exception.NoDocumentationFound
        ), wrapping.silence_printing():
            run_test.test(["build", "run", directory])

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

            with wrapping.silence_printing():
                run_test.test(["build", "run", directory])


def _make_current_rez_sphinx_context(extra_request=tuple(), package_paths=tuple()):
    """rez.resolved_context.ResolvedContext: Get the context for :ref:`rez_sphinx`."""
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


# TODO : Find a better way of doing this
def _watch(appender, function):
    """Run ``function`` and append its information to ``appender``."""
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)

        appender((args, kwargs, result))

        return result

    return wrapped


# TODO : Find a better way of doing this
@contextlib.contextmanager
def _watch_intersphinx_mapping():
    """Track the args, kwargs, and return results of key :ref:`rez_sphinx` functions."""
    original = bootstrap._merge_intersphinx_maps
    container = []

    bootstrap._merge_intersphinx_maps = _watch(
        container.append, bootstrap._merge_intersphinx_maps
    )

    try:
        yield container
    finally:
        bootstrap._merge_intersphinx_maps = original


# TODO : Find a better way of doing this
@contextlib.contextmanager
def _watch_candidates():
    """Track the args, kwargs, and return results of key :ref:`rez_sphinx` functions."""
    original = bootstrap._get_intersphinx_candidates
    container = []

    bootstrap._get_intersphinx_candidates = _watch(
        container.append, bootstrap._get_intersphinx_candidates
    )

    try:
        yield container
    finally:
        bootstrap._get_intersphinx_candidates = original


class Miscellaneous(unittest.TestCase):
    """Any test that doesn't make sense in other places."""

    @unittest.skipIf(
        not pypi_check.is_request_installed(_PYPI_RTD),
        "Install sphinx-rtd-theme with `rez-pip --install {_PYPI_RTD} --python-version=3`".format(
            _PYPI_RTD=_PYPI_RTD,
        ),
    )
    def test_sphinx_rtd_theme(self):
        """Ensure it's easy to install `sphinx-rtd-theme`_."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_api_pass_cli")

        creator.build(source_package, install_path, quiet=True)

        with wrapping.keep_cwd(), run_test.keep_config() as config:
            # Simulate the user adding sphinx-rtd-theme as a requirement and
            # then running rez_sphinx init / build.
            #
            # (Technically we only need the requirement :ref:`rez_sphinx build run`
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

            doc_test.add_to_default_text(source_directory)

            with wrapping.silence_printing():
                build = context.execute_command(
                    "rez_sphinx build run",
                    parent_environ=parent_environment,
                    stdout=open(os.devnull, "wb"),
                    stderr=open(os.devnull, "wb"),
                )
                build.communicate()

            self.assertEqual(0, init.returncode)
            self.assertEqual(0, build.returncode)

        with open(
            os.path.join(source_directory, "documentation", "build", "index.html"), "r"
        ) as handler:
            contents = handler.read()

        self.assertIn("Read the Docs", contents)

    def test_symlinks(self):
        """Ensure Rez packages with symlinked Python content build as expected."""
        # 1. Make the package
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_cli_argument")
        installed_package = creator.build(source_package, install_path, quiet=True)

        # 2. (Manually) build symlinks from the installed package to the source
        source_python_directory = os.path.join(source_directory, "python")
        destination = os.path.join(
            install_path,
            installed_package.name,
            str(installed_package.version),
            "python",
        )
        shutil.rmtree(destination)
        os.symlink(source_python_directory, destination)

        self.assertTrue(os.path.islink(destination))

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing(), run_test.allow_defaults():
                run_test.test(
                    'build run "{source_directory}" '
                    '--apidoc-arguments "--suffix .txt"'.format(
                        source_directory=source_directory
                    )
                )

        source = os.path.join(source_directory, "documentation", "source")

        self.assertEqual(
            {
                ".gitignore",
                "README",
                "modules.txt",
                "some_package.file.txt",
                "some_package.txt",
            },
            set(os.listdir(os.path.join(source, "api"))),
        )


class Options(unittest.TestCase):
    """Make sure options (CLI, rez-config, etc) work as expected."""

    def test_api_pass_cli(self):
        """Don't auto-build API documentation because the CLI said not to."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_test_api_pass_cli")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]), run_test.allow_defaults():
            run_test.test(["init", source_directory])

            with wrapping.silence_printing():
                run_test.test(["build", "run", source_directory, "--no-apidoc"])

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
                config.optionvars["rez_sphinx"]["init_options"] = dict()
                config.optionvars["rez_sphinx"]["sphinx-apidoc"] = dict()
                config.optionvars["rez_sphinx"]["init_options"][
                    "check_default_files"
                ] = False
                config.optionvars["rez_sphinx"]["sphinx-apidoc"][
                    "enable_apidoc"
                ] = False

                with wrapping.silence_printing():
                    run_test.test(["build", "run", source_directory])

        source = os.path.join(source_directory, "documentation", "source")
        api_directory = os.path.join(source, "api")

        self.assertFalse(os.path.isdir(api_directory))


class Runner(unittest.TestCase):
    """Make sure :ref:`rez_sphinx build run` works as expected."""

    def _hello_world_test(self):
        """Create a basic :ref:`rez_sphinx` "init + build"."""
        source_package = package_wrap.make_simple_developer_package()
        source_directory = finder.get_package_root(source_package)
        install_path = package_wrap.make_directory("_Build_hello_world_test")

        installed_package = creator.build(source_package, install_path, quiet=True)

        with run_test.simulate_resolve([installed_package]):
            run_test.test(["init", source_directory])

            with wrapping.silence_printing(), run_test.allow_defaults():
                run_test.test(["build", "run", source_directory])

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
        """Make sure `sphinx.ext.intersphinx`_ "sees" Rez packages as expected."""
        package_directories = package_wrap.make_dependent_packages()
        install_packages = [install for _, install in package_directories]
        watchers = []

        for source, install in package_directories:
            with run_test.simulate_resolve(install_packages), wrapping.keep_cwd():
                run_test.test(["init", source])

                with wrapping.silence_printing(), run_test.allow_defaults(), _watch_candidates() as watcher:
                    run_test.test(["build", "run", source])

                watchers.extend(watcher)

        # Whenever a DeveloperPackage is acquired or when a Rez package is
        # built, etc. The preprocess function is called. We expect the code to
        # run preprocess twice per :ref:`rez_sphinx build run` as a result (just
        # because that's what it happens to do).
        #
        # Multiply that by the number of builds and you get ``expected_times_called``
        #
        expected_times_called = len(package_directories) * 2

        self.assertEqual(4, expected_times_called)

        for args, _, results in watchers:
            package = args[0]

            if package.name != "a_package":
                continue

            self.assertEqual({"dependency", "python"}, results)
