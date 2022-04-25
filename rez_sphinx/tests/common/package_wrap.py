"""Miscellaneous functions for making Rez packages easier."""

import atexit
import functools
import io
import os
import shutil
import stat
import tempfile
import textwrap

from rez import developer_package
from rez.config import config
from rez_utilities import creator, finder

from rez_sphinx.core import generic


def _delete(path):
    """Delete ``path``, even if it's set to read-only."""

    def _remove_read_only(function, path, exception):
        os.chmod(path, stat.S_IWRITE)
        function(path)

    shutil.rmtree(path, onerror=_remove_read_only)


def _delete_later(directory):
    """Schedule ``directory`` for deletion.

    Args:
        directory (str): The absolute path to a folder on-disk to delete.

    """
    atexit.register(functools.partial(_delete, directory))


def make_dependent_packages():
    """Create a Rez package with a dependent package - both have documentation."""
    install_path = make_directory("_make_dependent_a_package_install_root")

    dependency_package = make_simple_developer_package(
        package_text=textwrap.dedent(
            """\
            name = "dependency"

            version = "2.0.0"

            requires = ["python"]

            build_command = "python {root}/rezbuild.py"

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join(root, "python"))
            """
        ),
        file_text=textwrap.dedent(
            '''\
            from dependency import file

            def some_function():
                """Run :func:`dependency.file.some_function`."""
                file.some_function()
            '''
        ),
    )

    installed_package_2 = creator.build(
        dependency_package,
        install_path,
        packages_path=[
            install_path,
            # !!! Remove all `release_packages_path` references, if possible
            config.release_packages_path,  # pylint: disable=no-member
        ],
        quiet=True,
    )

    source_package = make_simple_developer_package(
        package_text=textwrap.dedent(
            """\
            name = "a_package"

            version = "1.0.0"

            requires = ["python", "dependency-2"]

            build_command = "python {root}/rezbuild.py"

            def commands():
                import os

                env.PYTHONPATH.append(os.path.join(root, "python"))
            """
        ),
        file_text=textwrap.dedent(
            '''\
            from dependency import file

            def some_function():
                """Run :func:`dependency.file.some_function`."""
                file.some_function()
            '''
        ),
    )
    source_directory_1 = finder.get_package_root(source_package)

    installed_package_1 = creator.build(
        source_package,
        install_path,
        packages_path=[
            install_path,
            # !!! Remove all `release_packages_path` references, if possible
            config.release_packages_path,  # pylint: disable=no-member
        ],
        quiet=True,
    )

    source_directory_2 = finder.get_package_root(dependency_package)

    return [
        (source_directory_1, installed_package_1),
        (source_directory_2, installed_package_2),
    ]


def make_directory(name):
    """Make a directory with ``name`` and delete it later."""
    directory = tempfile.mkdtemp(suffix=name)
    _delete_later(directory)

    return directory


def make_package_configuration(configuration):
    """Create a Rez `package.py`_ with the given ``configuration``.

    Args:
        configuration (dict[str, object]):
            The override settings to apply to :ref:`rez_sphinx`.

    Returns:
        rez.developer_package.DeveloperPackage: The generated source Rez package.

    """
    directory = tempfile.mkdtemp(suffix="_make_package_config")
    atexit.register(functools.partial(_delete, directory))

    template = textwrap.dedent(
        """\
        name = "foo"

        version = "1.0.0"

        rez_sphinx_configuration = {configuration!r}
        """
    )

    with io.open(
        os.path.join(directory, "package.py"),
        "w",
        encoding="utf-8",
    ) as handler:
        handler.write(generic.decode(template.format(configuration=configuration)))

    return developer_package.DeveloperPackage.from_path(directory)


def make_rez_configuration(text):
    """str: Create a rezconfig.py, using ``text``."""
    directory = make_directory("make_rez_configuration")
    configuration = os.path.join(directory, "rezconfig.py")

    with io.open(configuration, "w", encoding="utf-8") as handler:
        handler.write(generic.decode(text))

    return configuration


def make_simple_developer_package(package_text="", file_text="", help_=None):
    """Create a simple Rez source package.

    Args:
        package_text (str, optional):
            The source code for the source Rez package.
        file_text (str, optional):
            Some example Python source file within this pretend source Rez package.
        help_ (list[list[str, str]] or str or None, optional):
            The initial Rez package `package help`_. If ``None``, no
            ``help`` will be defined. All other input is used as-is. This
            data, if provided, is appended directly to ``package_text``.

    Returns:
        rez.packages.Package: The found, generated main source Rez package.

    """
    directory = make_directory("_make_simple_developer_package_source_package")

    package_text = package_text or textwrap.dedent(
        """\
        name = "some_package"

        version = "1.0.0"

        requires = ["python"]

        build_command = "python {root}/rezbuild.py"

        def commands():
            import os

            env.PYTHONPATH.append(os.path.join(root, "python"))
        """
    )

    if help_ is not None:
        package_text += "\nhelp = {help_!r}".format(help_=help_)

    file_text = file_text or textwrap.dedent(
        '''\
        def some_function():
            """Do a function."""
        '''
    )

    file_text = generic.decode(file_text)
    package_text = generic.decode(package_text)

    with io.open(
        os.path.join(directory, "package.py"), "w", encoding="utf-8"
    ) as handler:
        handler.write(package_text)

    with io.open(
        os.path.join(directory, "rezbuild.py"), "w", encoding="utf-8"
    ) as handler:
        handler.write(
            generic.decode(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python
                    # -*- coding: utf-8 -*-

                    import os
                    import shutil


                    def build(source, destination, items):
                        shutil.rmtree(destination)
                        os.makedirs(destination)

                        for item in items:
                            source_path = os.path.join(source, item)
                            destination_path = os.path.join(destination, item)

                            if os.path.isdir(source_path):
                                shutil.copytree(source_path, destination_path)
                            elif os.path.isfile(source_path):
                                shutil.copy2(source_path, destination_path)


                    if __name__ == "__main__":
                        build(
                            os.environ["REZ_BUILD_SOURCE_PATH"],
                            os.environ["REZ_BUILD_INSTALL_PATH"],
                            {"python"},
                        )
                    """
                )
            )
        )

    python_directory = os.path.join(directory, "python")
    os.makedirs(python_directory)

    package = finder.get_nearest_rez_package(directory)
    python_package = os.path.join(python_directory, package.name)

    os.makedirs(python_package)

    with io.open(os.path.join(python_package, "__init__.py"), "a", encoding="utf-8"):
        pass

    with io.open(
        os.path.join(python_package, "file.py"), "w", encoding="utf-8"
    ) as handler:
        handler.write(file_text)

    return package
