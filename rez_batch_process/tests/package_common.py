#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A set of functions to make creating Rez packages / repositories in unittests easier."""

import os
import shutil
import tempfile
import textwrap

import git
from python_compatibility.testing import common
from rez import packages_
from rez_batch_process.core import worker
from rez_utilities import creator, inspection
from six.moves import mock


class Tests(common.Common):
    """A common class used to test everything in this module."""

    def _test(self, expected, packages, paths=None):
        """Check that `packages`, when processed, equals `expected`.

        Args:
            expected (object): The output of `packages` after :func:`.fix` has been run.
            packages (:class:`rez.developer_package.DeveloperPackage`):
                The Rez packages that will be processed.
            paths (list[str], optional): The locations on-disk that
                will be used to any Rez-environment-related work. Some
                plugins need these paths for resolving a context, for
                example. Default is None.

        """
        arguments = mock.MagicMock()
        arguments.command = "echo 'foo'"
        arguments.pull_request_prefix = "ticket-name"
        arguments.exit_on_error = True
        _, unfixed, invalids, skips = worker.fix(packages, arguments, paths=paths)
        self.assertEqual(expected, (unfixed, invalids, skips))


def _make_python_rezbuild(path):
    """Create a generic "rezbuild.py" that a fake Rez python package can build/install to.

    Args:
        path (str): The path on-disk that the new file will be written to.

    """
    with open(path, "w") as handler:
        handler.write(
            textwrap.dedent(
                '''\
                #!/usr/bin/env python
                # -*- coding: utf-8 -*-

                """The main module which installs a Python package onto the user's system."""

                # IMPORT STANDARD LIBRARIES
                import os
                import shutil
                import sys


                def build(source_path, install_path):
                    for folder in ("python", ):
                        destination = os.path.join(install_path, folder)

                        if os.path.isdir(destination):
                            shutil.rmtree(destination)

                        source = os.path.join(source_path, folder)

                        shutil.copytree(source, destination)


                if __name__ == "__main__":
                    build(
                        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
                        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
                    )
                '''
            )
        )


def make_build_python_package(text, name, version, root):
    """Create a Rez-python package and build it to a temporary directory.

    Args:
        text (str): The contents of the package.py file that will be created.
        name (str): The name of the Rez package.
        version (str): The major, minor, and patch information for the Rez package. e.g. "1.0.0".
        root (str): An absolute folder on-disk where the package.py will be written to.

    Returns:
        :class:`rez.developer_package.DeveloperPackage`: The built package.

    """
    package = make_source_python_package(text, name, version, root)
    build_directory = tempfile.mkdtemp(suffix="_build_python_package")
    source_package = packages_.get_developer_package(os.path.dirname(package))

    return creator.build(source_package, build_directory).filepath


def make_fake_repository(packages, root):
    """Create a new git repository that contains the given Rez packages.

    This function is a bit hacky. It creates a git repository, which
    is fine, but Rez packages create "in-memory" packages based on
    actual package.py files on-disk. So the packages need to copied
    to the folder where the repository was created and "re-queried"
    in order to be "true" developer Rez packages. If there was a way
    to easily create a developer Rez package, I'd do that. But meh,
    too much work.

    Args:
        packages (iter[:class:`rez.developer_package.DeveloperPackage`]):
            The Rez packages that will be copied into the new git repository.
        root (str): The folder on-disk that represents the top-level folder
            for every Rez package in `packages`.

    Returns:
        tuple[:class:`git.Repo`, list[:class:`rez.developer_package.DeveloperPackage`]]:
            The newly created repository + the Rez packages that got copied into it.

    """
    repository_root = os.path.join(
        tempfile.mkdtemp(suffix="_clone_repository"), "test_folder"
    )
    os.makedirs(repository_root)

    initialized_packages = []

    for package in packages:
        package_root = inspection.get_package_root(package)
        relative = os.path.relpath(package_root, root)
        destination = os.path.join(repository_root, relative)
        parent = os.path.dirname(destination)

        if not os.path.isdir(parent):
            os.makedirs(parent)

        shutil.copytree(package_root, destination)

        initialized_packages.append(packages_.get_developer_package(destination))

    remote_root = tempfile.mkdtemp(suffix="_remote_bare_repository")
    shutil.rmtree(
        remote_root
    )  # I just need the folder name. The directory should not exist
    remote_root += ".git"  # bare repositories, by convention, end in ".git"
    remote = git.Repo.init(remote_root, bare=True)

    repository = git.Repo.init(repository_root)
    repository.index.add(
        [item for item in os.listdir(repository_root) if item != ".git"]
    )
    repository.index.commit("initial commit")
    repository.create_remote("origin", url=remote.working_dir)
    origin = repository.remotes.origin
    origin.push(refspec="master:master")
    repository.heads.master.set_tracking_branch(
        origin.refs.master
    )  # set local "master" to track remote "master

    return repository, initialized_packages, remote_root


def make_package(  # pylint: disable=too-many-arguments
    name, root, builder, version="1.0.0", dependencies=frozenset(), variants=None
):
    """Make a source Rez package and its initial files.

    Args:
        name (str):
            The name of the Rez package that will be created.
        root (str):
            An absolute folder on-disk where the package.py will be written to.
        builder (callable[str, str, str, str] -> str):
            The function that is used to generate the "contents" of the
            Rez package. This function is only responsible for creating
            the package.py/rezbuild.py files, it doesn't create a Python
            package, for example. This parameter is responsible for
            creating the rest of the files of the package.
        version (str, optional):
            The major, minor, and patch information for the Rez package. Default: "1.0.0".
        dependencies (set[str]):
            The Rez package requirements for this package. e.g. {"project_a-1+"}.
            Default is empty.
        variants (list[list[str]]):
            The extra Rez package build configurations for this package.
            No variants will be installed if nothing is given. Default
            is None.

    Returns:
        :class:`rez.developer_package.DeveloperPackage`: The generated Rez package.

    """
    template = textwrap.dedent(
        """\
        name = "{name}"
        version = "{version}"
        requires = {requires}

        build_command = "echo 'do nothing'"
        """
    )

    requires = ", ".join(
        ['"{name}"'.format(name=dependency) for dependency in dependencies]
    )
    requires = "[{requires}]".format(requires=requires)

    if variants:
        template += "\nvariants = {variants!r}"

    text = template.format(
        name=name, version=version, requires=requires, variants=variants
    )
    package_file = builder(text, name, version, root)

    return packages_.get_developer_package(os.path.dirname(package_file))


def make_source_package(text, name, _, root):
    """Create a source Rez package using the given input.

    Args:
        text (str): The contents of the package.py file that will be created.
        name (str): The name of the Rez package.
        root (str): An absolute folder on-disk where the package.py will be written to.

    Returns:
        str: The full path on-disk where the package.py file is written to.

    """
    directory = os.path.join(root, name)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(text)

    return handler.name


def make_source_python_package(text, name, version, root):
    """Create a source Rez package that contains a Python package, using the given input.

    Args:
        text (str): The contents of the package.py file that will be created.
        name (str): The name of the Rez package.
        version (str): The major, minor, and patch information for the Rez package. e.g. "1.0.0".
        root (str): An absolute folder on-disk where the package.py will be written to.

    Returns:
        str: The full path on-disk where the package.py file is written to.

    """
    path = make_source_package(text, name, version, root)
    directory = os.path.dirname(path)

    with open(path, "a") as handler:
        handler.write(
            textwrap.dedent(
                """
                build_command = "python {root}/rezbuild.py {install}"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join("{root}", "python"))
                """
            )
        )

    _make_python_rezbuild(os.path.join(directory, "rezbuild.py"))
    os.makedirs(os.path.join(directory, "python"))
    open(os.path.join(directory, "python", "some_module.py"), "a").close()

    return path


def make_source_variant_python_package(text, name, version, root):
    """Create a Rez package that is not built. And the package has at least one variant.

    Args:
        text (str): The contents of the package.py file that will be created.
        name (str): The name of the Rez package.
        version (str): The major, minor, and patch information for the Rez package. e.g. "1.0.0".
        root (str): An absolute folder on-disk where the package.py will be written to.

    Returns:
        str: The full path on-disk where the package.py file is written to.

    """
    package = make_source_python_package(text, name, version, root)

    with open(package, "a") as handler:
        handler.write('\nvariants = [["python-2.7"]]')

    return package