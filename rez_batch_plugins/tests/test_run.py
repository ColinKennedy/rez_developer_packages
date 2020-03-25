#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Check that the plugin commands the ``rez_batch_plugins`` defines work as-expected."""

import collections
import functools
import operator
import os
import shlex
import sys
import tempfile
import textwrap

from python_compatibility import pathrip
from python_compatibility.testing import common
from rez import serialise
from rez_batch_plugins import repository_area
from rez_batch_plugins.plugins import bump, move_imports, yaml2py
from rez_batch_process.core import registry, worker
from rez_utilities import creator, inspection, rez_configuration
from rez_utilities_git import testify
from six.moves import mock


class Bugs(common.Common):
    """Fix bugs that have come up while searching through Rez packages."""

    @mock.patch("rez_batch_plugins.repository_area._is_keep_temporary_files_enabled")
    @mock.patch("rez_batch_plugins.repository_area._get_temporary_directory")
    def test_is_definition_build_package(self, _get_temporary_directory, _is_keep_temporary_files_enabled):
        """Fix an issue where git repositories with "built" Rez packages cause cyclic loops."""
        def _make_built_package(root):
            directory = os.path.join(root, "1.0.0")
            os.makedirs(directory)

            with open(os.path.join(directory, "package.py"), "w") as handler:
                handler.write(
                    textwrap.dedent(
                        """\
                        name = "something"
                        version = "1.0.0"
                        """
                    )
                )

            return inspection.get_nearest_rez_package(directory)

        _is_keep_temporary_files_enabled.return_value = False
        _get_temporary_directory.return_value = tempfile.mkdtemp(suffix="_temporary_directory")
        root = tempfile.mkdtemp(suffix="_test_is_definition_build_package")
        self.delete_item_later(root)

        package = _make_built_package(root)
        repository, packages, remote_root = testify.make_fake_repository([package], root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        self.assertFalse(repository_area.is_definition(packages[0], serialise.FileFormat.yaml))


class MoveImports(common.Common):
    """Check that the :mod:`rez_batch_plugins.plugins.move_imports` plugin works correctly."""

    @classmethod
    def setUpClass(cls):
        """Add some generic plugins so that tests have something to work with."""
        super(MoveImports, cls).setUpClass()

        _clear_registry()
        move_imports.main()

    @classmethod
    def tearDownClass(cls):
        """Remove all stored plugins."""
        super(MoveImports, cls).tearDownClass()

        _clear_registry()

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )  # pylint: disable=too-many-locals
    def test_no_change(self, _create_pull_request):
        """Don't change the imports of any Rez package or file."""
        root = tempfile.mktemp(suffix="_test_single_change_source_packages")
        self.delete_item_later(root)

        packages = [
            _make_package_with_modules(  # This package won't be changed
                "a_unchanging_package",
                [
                    (
                        os.path.join("in", "folder", "some_module.py"),
                        textwrap.dedent(
                            """\
                            import os
                            import textwrap

                            def foo():
                                import shlex
                            """
                        ),
                    ),
                    ("another_file.py", ""),
                    (
                        "more_files.py",
                        textwrap.dedent(
                            """\
                            import custom.namespace
                            from blah import here, there, everywhere
                            """
                        ),
                    ),
                ],
                root,
            )
        ]

        repository, packages, remote_root = testify.make_fake_repository(packages, root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        release_path = tempfile.mkdtemp(suffix="_a_release_location_for_testing")
        options, parser = _make_fake_release_data()

        for package in packages:
            creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
                search_paths=[repository.working_dir],
                quiet=True,
            )

        move_imports_arguments, text = _get_test_commands()

        text = shlex.split(text)
        sys.argv[1:] = text

        arguments = _Arguments(move_imports_arguments, text)

        with rez_configuration.patch_release_packages_path(release_path):
            _, unfixed, invalids, skips = _get_test_results(
                "move_imports", arguments=arguments
            )

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [("a_unchanging_package", "No namespaces need to be replaced.")],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        self.assertEqual(0, _create_pull_request.call_count)

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )  # pylint: disable=too-many-locals
    def test_single_change(self, _create_pull_request):
        """Change only one package.

        Raises:
            RuntimeError: If an expected cloned file does not exist.

        """
        root = tempfile.mktemp(suffix="_test_single_change_source_packages")
        self.delete_item_later(root)

        packages = [
            _make_package_with_modules(  # This package will end up getting changed
                "some_package",
                [
                    (
                        os.path.join("in", "folder", "some_module.py"),
                        textwrap.dedent(
                            """\
                            if True:
                                from some.namespace import here, there, everywhere
                            """
                        ),
                    )
                ],
                root,
            ),
            _make_package_with_modules(  # This package won't be changed
                "a_unchanging_package",
                [
                    (
                        os.path.join("in", "folder", "some_module.py"),
                        textwrap.dedent(
                            """\
                            import os
                            import textwrap

                            def foo():
                                import shlex
                            """
                        ),
                    ),
                    ("another_file.py", ""),
                    (
                        "more_files.py",
                        textwrap.dedent(
                            """\
                            import custom.namespace
                            from blah import here, there, everywhere
                            """
                        ),
                    ),
                ],
                root,
            ),
        ]

        repository, packages, remote_root = testify.make_fake_repository(packages, root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        release_path = tempfile.mkdtemp(suffix="_a_release_location_for_testing")
        options, parser = _make_fake_release_data()

        for package in packages:
            creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
                search_paths=[repository.working_dir],
                quiet=True,
            )

        move_imports_arguments, text = _get_test_commands()

        text = shlex.split(text)
        sys.argv[1:] = text

        arguments = _Arguments(move_imports_arguments, text)

        with rez_configuration.patch_release_packages_path(release_path):
            processed_packages, unfixed, invalids, skips = _get_test_results(
                "move_imports", arguments=arguments
            )

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [("a_unchanging_package", "No namespaces need to be replaced.")],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        cloned_package = inspection.get_package_root(next(iter(processed_packages)))
        path = os.path.join(cloned_package, "python", "in", "folder", "some_module.py")

        if not os.path.isfile(path):
            raise RuntimeError('Path "{path}" does not exist.'.format(path=path))

        with open(path, "r") as handler:
            code = handler.read()

        expected = textwrap.dedent(
            """\
            if True:
                from a.new.space import somewhere
                from some.namespace import there, everywhere
            """
        )

        self.assertEqual(expected, code)
        self.assertEqual(1, _create_pull_request.call_count)

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )  # pylint: disable=too-many-locals
    def test_multiple_changes(self, _create_pull_request):
        """Change 2+ packages at once."""
        root = tempfile.mktemp(suffix="_test_single_change_source_packages")
        self.delete_item_later(root)

        packages = [
            _make_package_with_modules(  # This package will end up getting changed
                "some_package",
                [
                    (
                        os.path.join("in", "folder", "some_module.py"),
                        textwrap.dedent(
                            """\
                            if True:
                                from some.namespace import here, there, everywhere
                            """
                        ),
                    )
                ],
                root,
            ),
            _make_package_with_modules(  # This package will also be changed
                "another_package",
                [
                    (
                        os.path.join("a_folder", "a_file.py"),
                        textwrap.dedent(
                            """\
                            import os, textwrap, some.namespace.here, another_one.here
                            """
                        ),
                    ),
                    ("another_file.py", ""),
                    (
                        "more_files.py",
                        textwrap.dedent(
                            """\
                            import custom.namespace
                            from blah import here, there, everywhere
                            """
                        ),
                    ),
                ],
                root,
            ),
        ]

        repository, packages, remote_root = testify.make_fake_repository(packages, root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        release_path = tempfile.mkdtemp(suffix="_a_release_location_for_testing")
        options, parser = _make_fake_release_data()

        for package in packages:
            creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
                search_paths=[repository.working_dir],
                quiet=True,
            )

        move_imports_arguments, text = _get_test_commands()

        text = shlex.split(text)
        sys.argv[1:] = text

        arguments = _Arguments(move_imports_arguments, text)

        with rez_configuration.patch_release_packages_path(release_path):
            processed_packages, unfixed, invalids, skips = _get_test_results(
                "move_imports", arguments=arguments
            )

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual([], skips)

        processed_packages = sorted(processed_packages, key=operator.attrgetter("name"))
        cloned_package = inspection.get_package_root(processed_packages[1])
        path = os.path.join(cloned_package, "python", "in", "folder", "some_module.py")

        if not os.path.isfile(path):
            raise RuntimeError('Path "{path}" does not exist.'.format(path=path))

        with open(path, "r") as handler:
            code_package_1 = handler.read()

        expected_package_1 = textwrap.dedent(
            """\
            if True:
                from a.new.space import somewhere
                from some.namespace import there, everywhere
            """
        )

        cloned_package = inspection.get_package_root(processed_packages[0])
        path = os.path.join(cloned_package, "python", "a_folder", "a_file.py")

        if not os.path.isfile(path):
            raise RuntimeError('Path "{path}" does not exist.'.format(path=path))

        with open(path, "r") as handler:
            code = handler.read()

        expected = textwrap.dedent(
            """\
            import os, textwrap, a.new.space.somewhere, another_one.here
            """
        )

        self.assertEqual(expected_package_1, code_package_1)
        self.assertEqual(expected, code)

        self.assertEqual(2, _create_pull_request.call_count)


class Yaml2Py(common.Common):
    """Check that the :mod:`rez_batch_plugins.plugins.yaml2py` plugin works correctly."""

    @classmethod
    def setUpClass(cls):
        """Add some generic plugins so that tests have something to work with."""
        super(Yaml2Py, cls).setUpClass()

        _clear_registry()
        yaml2py.main()

    @classmethod
    def tearDownClass(cls):
        """Remove all stored plugins."""
        super(Yaml2Py, cls).tearDownClass()

        _clear_registry()

    def _make_fake_released_packages(self, other_package):
        """Create 2 basic Rez packages to use for testing.

        Args:
            other_package (str):
                If "yaml", one of the packages created will be a
                package.yaml file. Otherwise, it gets added as a
                package.py file.

        Returns:
            str: The path where all of the created packages will go to.

        """
        root = tempfile.mkdtemp(suffix="_test_replace_yaml")
        self.delete_item_later(root)

        packages = [
            _make_rez_package(
                "another_package",
                "package.py",
                textwrap.dedent(
                    """\
                    name = "another_package"
                    version = "1.2.0"
                    description = "A package.py Rez package that won't be converted."
                    build_command = "echo 'foo'"
                    """
                ),
                root,
            )
        ]

        if other_package == "yaml":
            packages.append(
                _make_rez_package(
                    "some_package",
                    "package.yaml",
                    textwrap.dedent(
                        """\
                        name: some_package
                        version: 1.2.0
                        description: "A YAML-based package that will be converted."
                        build_command: "echo 'foo'"
                        """
                    ),
                    root,
                )
            )
        else:
            packages.append(
                _make_rez_package(
                    "some_package",
                    "package.py",
                    textwrap.dedent(
                        """\
                        name = "some_package"
                        version = "1.2.0"
                        description = "A YAML-based package that will be converted."
                        build_command = "echo 'foo'"
                        """
                    ),
                    root,
                )
            )

        repository, packages, remote_root = testify.make_fake_repository(packages, root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        release_path = tempfile.mkdtemp(suffix="_some_release_location")
        self.delete_item_later(release_path)

        options, parser = _make_fake_release_data()

        for package in packages:
            creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
                search_paths=[repository.working_dir],
                quiet=True,
            )

        return release_path

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )
    def test_no_replace(self, _create_pull_request):
        """Don't replace anything because no package is package.yaml."""
        release_path = self._make_fake_released_packages("py")

        text = shlex.split("run yaml2py fake_pr_prefix fake-github-access-token")
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            _, unfixed, invalids, skips = _get_test_results("yaml2py")

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [
                ("another_package", "is not a package.yaml file."),
                ("some_package", "is not a package.yaml file."),
            ],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        self.assertEqual(0, _create_pull_request.call_count)

    @mock.patch(
        "rez_batch_process.core.plugins.command.RezShellCommand._create_pull_request"
    )
    def test_replace_yaml(self, _create_pull_request):
        """Replace one package.yaml with package.py and don't touch the other package."""
        release_path = self._make_fake_released_packages("yaml")

        text = shlex.split("run yaml2py fake_pr_prefix fake-github-access-token")
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            _, unfixed, invalids, skips = _get_test_results("yaml2py")

        self.assertEqual(set(), unfixed)
        self.assertEqual([], invalids)
        self.assertEqual(
            [("another_package", "is not a package.yaml file.")],
            [(skip.package.name, skip.reason) for skip in skips],
        )

        self.assertEqual(1, _create_pull_request.call_count)


class Bump(common.Common):
    """Check that the :mod:`rez_batch_plugins.plugins.bump` plugin works correctly."""

    @classmethod
    def setUpClass(cls):
        """Add some generic plugins so that tests have something to work with."""
        super(Bump, cls).setUpClass()

        _clear_registry()
        bump.main()

    @classmethod
    def tearDownClass(cls):
        """Remove all stored plugins."""
        super(Bump, cls).tearDownClass()

        _clear_registry()

    # def test_source(self):
    #     """Bump a source Rez package."""
    #     pass
    #
    # def test_built_symlink(self):
    #     """Bump a built Rez package that is symlinked to a Rez package within a git repository."""
    #     pass
    #
    # def test_released(self):
    #     """Bump a released Rez package that points to a git repository."""
    #     pass

    def test_egg(self):
        """Bump a released Rez package which only contains a single zipped .egg file."""
        class _Arguments(object):
            instructions = "Do something!"
            new = "minor"
            packages = ["another_package"]
            pull_request_name = "PR"
            token = "github-token"
            additional_paths = []

        def _create_package(root, name, requirements=None):
            text = textwrap.dedent(
                """\
                name = "{name}"
                version = "1.2.0"
                description = "A package.py Rez package that won't be converted."
                build_command = "python {{root}}/rezbuild.py"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{{root}}", "python.egg"))
                """
            )

            text = text.format(name=name)

            if requirements:
                text += "\nrequires = {requirements!r}".format(requirements=requirements)

            with open(os.path.join(root, "package.py"), "w") as handler:
                handler.write(text)

            with open(os.path.join(root, "rezbuild.py"), "w") as handler:
                handler.write(
                    textwrap.dedent(
                        """\
                        #!/usr/bin/env python
                        # -*- coding: utf-8 -*-

                        import os
                        import shutil
                        import zipfile


                        def main():
                            source = os.environ["REZ_BUILD_SOURCE_PATH"]
                            build = os.environ["REZ_BUILD_PATH"]

                            python_directory = os.path.join(source, "python")

                            with zipfile.ZipFile(os.path.join(build, "python.egg"), "w") as handler:
                                for root, folders, files in os.walk(python_directory):
                                    relative_root = os.path.relpath(root, python_directory)

                                    for folder in folders:
                                        handler.write(os.path.join(root, folder), os.path.join(relative_root, folder))

                                    for file_ in files:
                                        handler.write(os.path.join(root, file_), os.path.join(relative_root, file_))

                            shutil.copy2(
                                handler.filename,
                                os.path.join(os.environ["REZ_BUILD_INSTALL_PATH"], os.path.basename(handler.filename)),
                            )


                        if __name__ == "__main__":
                            main()
                        """
                    )
                )
            os.makedirs(os.path.join(root, "python"))

        def _make_package_with_contents(root, name, create_package):
            directory = os.path.join(root, name)
            os.makedirs(directory)

            create_package(directory)

            return inspection.get_nearest_rez_package(directory)

        root = tempfile.mkdtemp(suffix="_test_is_definition_build_package")
        self.delete_item_later(root)

        packages = [
            _make_package_with_contents(root, "some_package", _create_package)
        ]

        repository, packages, remote_root = testify.make_fake_repository(packages, root)
        self.delete_item_later(repository.working_dir)
        self.delete_item_later(remote_root)

        release_path = tempfile.mkdtemp(suffix="_a_release_location_for_testing")
        self.delete_item_later(release_path)
        options, parser = _make_fake_release_data()

        for package in packages:
            creator.release(
                inspection.get_package_root(package),
                options,
                parser,
                release_path,
                search_paths=[repository.working_dir],
                quiet=True,
            )

        text = 'PR github-token --packages another_package --instructions "Do it!" --new minor'

        text = shlex.split(text)
        sys.argv[1:] = text

        with rez_configuration.patch_release_packages_path(release_path):
            _, unfixed, invalids, skips = _get_test_results(
                "bump", arguments=_Arguments
            )


class _Arguments(object):  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self, arguments, command):
        super(_Arguments, self).__init__()

        self.token = "github-token-here"
        self.pull_request_name = "some_git_branch_name"
        self.ssl_no_verify = False
        self.cached_users = ""
        self.fallback_reviewers = ""
        self.base_url = ""
        self.arguments = arguments
        self.command = command
        self.exit_on_error = True


def _clear_registry():
    for name in registry.get_plugin_keys():
        registry.clear_plugin(name)

    for name in registry.get_command_keys():
        registry.clear_command(name)


def _make_fake_release_data():
    """Make the required arguments needed for rez-release to work."""
    options = mock.MagicMock()
    options.cmd = "release"
    options.debug = False
    options.message = "Fake release message"
    options.no_message = False
    options.process = "local"
    options.variants = None
    options.vcs = None

    parser = mock.MagicMock()
    parser.prog = "rez release"

    return options, parser


def _make_package_with_modules(name, modules, root):
    def _add_init(directory):
        open(os.path.join(directory, "__init__.py"), "a").close()

    def _make_parent_python_folders(directory, root):
        paths = []

        for token in pathrip.split_os_path_asunder(directory):
            paths.append(token)

            folder = os.path.join(root, *paths)

            if not os.path.isdir(folder):
                os.makedirs(folder)
                _add_init(folder)

    template = textwrap.dedent(
        """\
        name = "{name}"

        version = "1.2.0"

        build_command = "python {{root}}/rezbuild.py"

        def commands():
            import os

            env.PYTHONPATH.append(os.path.join("{{root}}", "python"))
        """
    )

    directory = os.path.join(root, name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(template.format(name=name))

    with open(os.path.join(directory, "rezbuild.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                import shutil
                import os

                def main(source, install):
                    shutil.copytree(os.path.join(source, "python"), os.path.join(install, "python"))

                if __name__ == "__main__":
                    main(
                        os.environ["REZ_BUILD_SOURCE_PATH"],
                        os.environ["REZ_BUILD_INSTALL_PATH"],
                    )
                """
            )
        )

    python_root = os.path.join(directory, "python")
    os.makedirs(python_root)

    _add_init(python_root)

    for path, text in modules:
        full_path = os.path.join(python_root, path)
        path_directory = os.path.dirname(full_path)
        _make_parent_python_folders(path_directory, python_root)

        with open(full_path, "w") as handler:
            handler.write(text)

    return inspection.get_nearest_rez_package(directory)


def _make_rez_package(name, package_name, text, root):
    """Create a package.py or package.yaml Rez package file.

    Args:
        name (str): The Rez package family name.
        package_name (str): Use "package.py" or "package.yaml" here.
        text (str): The contents of the created file.
        root (str): A directory where the newly created file will be written to.

    Returns:
        :class:`rez.packages_.DeveloperPackage`: The generated Rez package.

    """
    directory = os.path.join(root, name)
    os.makedirs(directory)

    with open(os.path.join(directory, package_name), "w") as handler:
        handler.write(text)

    return inspection.get_nearest_rez_package(directory)


def _get_test_commands():
    move_imports_arguments = "'. some.namespace.here,a.new.space.somewhere' --deprecate 'original_requirement-1,some.namespace' --requirements 'a_new_package-3.1+<4,a.new.space'"  # pylint: disable=line-too-long
    text = 'run move_imports --arguments "{move_imports_arguments}" pr_prefix github-token --why "Because we must"'.format(  # pylint: disable=line-too-long
        move_imports_arguments=move_imports_arguments
    )

    return move_imports_arguments, text


def _get_test_results(command_text, paths=None, arguments=None):
    """Get the conditions for a test (but don't actually run unittest.

    Args:
        command_text (str):
            Usually "shell", "yaml2py", "move_imports", etc. This string
            will find and modify Rez packages based on some registered
            plugin.
        paths (list[str], optional):
            The locations on-disk that will be used to any
            Rez-environment-related work. Some plugins need these paths
            for resolving a context, for example. Default is None.

    Returns:
        The output of :func:`rez_batch_process.core.worker.run`.

    """
    if not arguments:
        arguments = mock.MagicMock()

    finder = registry.get_package_finder(command_text)
    valid_packages, invalid_packages, skips = finder(paths=paths)

    command = registry.get_command(command_text)

    final_packages, unfixed, invalids = worker.run(
        functools.partial(command.run, arguments=arguments),
        valid_packages,
        keep_temporary_files=True,
    )

    invalids.extend(invalid_packages)

    return (final_packages, unfixed, invalids, skips)
