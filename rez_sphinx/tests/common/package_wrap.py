import atexit
import functools
import os
import shutil
import tempfile
import textwrap

from rez.config import config
from rez_utilities import creator, finder


def _delete_later(directory):
    atexit.register(functools.partial(shutil.rmtree, directory))


def make_directory(name):
    """Make a directory with ``name`` and delete it later."""
    directory = tempfile.mkdtemp(suffix=name)
    # _delete_later(directory)

    return directory


def make_dependent_packages():
    """Create a Rez package that depends on another package - both have documentation."""
    install_path = make_directory("_make_dependent_a_package_install_root")

    # TODO : Add a proper python package or find a way to build without it
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
        packages_path=[install_path, config.release_packages_path],
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
        packages_path=[install_path, config.release_packages_path],
    )

    source_directory_2 = finder.get_package_root(dependency_package)

    return [
        (source_directory_1, installed_package_1),
        (source_directory_2, installed_package_2),
    ]


def make_simple_developer_package(package_text="", file_text=""):
    """:class:`rez.developer_package.DeveloperPackage`: A simple Rez source package."""
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

    file_text = file_text or textwrap.dedent(
        '''\
        def some_function():
            """Do a function."""
        '''
    )

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(package_text)

    with open(os.path.join(directory, "rezbuild.py"), "w") as handler:
        handler.write(
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

    python_directory = os.path.join(directory, "python")
    os.makedirs(python_directory)

    package = finder.get_nearest_rez_package(directory)
    python_package = os.path.join(python_directory, package.name)

    os.makedirs(python_package)
    open(os.path.join(python_package, "__init__.py"), "a").close()

    with open(os.path.join(python_package, "file.py"), "w") as handler:
        handler.write(file_text)

    return package
