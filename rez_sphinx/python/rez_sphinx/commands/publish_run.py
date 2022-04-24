"""The module which handles the :ref:`rez_sphinx publish run` command."""

import argparse
import logging
import shlex

import six
from rez_utilities import finder
from rez import package_test

from .. import _cli_build
from ..core import exception
from ..preferences import preference
from .builder import runner as runner_

_LOGGER = logging.getLogger(__name__)
_SUCCESS_EXIT_CODE = 0
_REZ_TEST_COMMAND_KEY = "command"


def _get_documentation_destination(name, package):
    """Find the directory where built documentation now lives.

    This function assumes that ``name`` has already been run at least once.

    Args:
        name (str):
            The name of the Rez `tests`_ key that ran.
        package (rez.packages.Package):
            The package which defines `name`_ and was ran from.

    Returns:
        str: The found documentation build directory.

    """

    def _parse_destination(text):
        command = shlex.split(text)[1:]
        namespace = _parse_build_command(command)

        _, documentation_source = runner_.get_documentation_source(namespace.directory)
        documentation_build = runner_.get_documentation_build(documentation_source)

        return documentation_build

    test = package.tests[name]

    if isinstance(test, six.string_types):
        return _parse_destination(test)

    return _parse_destination(test[_REZ_TEST_COMMAND_KEY])


def _parse_build_command(command):
    """Parse the given :ref:`build_documentation_key` command.

    Args:
        command (list[str]):
            Raw user text to parse, separated by spaces. e.g. ``["build", "run"]``.

    Returns:
        argparse.Namespace: The parsed ``command``, as arguments.

    """
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(
        dest="command",
        description="All available rez_sphinx commands. Provide a name here.",
    )
    sub_parsers.required = True

    _cli_build.set_up_build(parser)

    return parser.parse_args(command)


def _validated_test_keys(runner):
    """Get every :ref:`rez_sphinx`-registered `tests`_ key in ``runner``.

    Since :ref:`rez_sphinx.build_documentation_key` may be multiple values, we
    must check and return every matching key in ``runner``.

    Args:
        runner (rez.package_test.PackageTestRunner): The Rez package to query from.

    Returns:
        list[str]:
            Every found, matching key. In most cases, this will return either
            ``["build_documentation"]``, which is the default
            :ref:`rez_sphinx.build_documentation_key`, or nothing.

    """
    tests = runner.get_test_names()

    if not tests:
        return []

    package = runner.get_package()

    # TODO : It may make more sense to add a
    # `preference.get_publish_documentation_keys` and have that list default to
    # `preference.get_build_documentation_keys` if it is not defined. That way
    # users can specify publish keys differently than build ones.
    #
    build_tests = preference.get_build_documentation_keys(package=package)
    names = [name for name in build_tests if name in tests]

    return names


def get_all_publishers(package):
    """Find every registered publisher for ``package``.

    Every found publisher will be auto-connected to the remote git repository
    that they're associated with (e.g. `GitHub`_).

    Args:
        package (rez.packages.Package):
            A package which may contain extra configuration overrides.
            Any override not found will be retrieved globally.

    Returns:
        list[Publisher]: Every registered publish method.

    """
    # Note: This inner import is because it's not a guarantee that users have
    # rez_docbot loaded as a plugin. They need to include:
    #
    # ".rez_sphinx.feature.docbot_plugin-1"
    #
    # in their resolves for this import to work.
    #
    from rez_docbot import api  # pylint: disable=import-outside-toplevel

    publishers = api.get_all_publishers(package)

    for publisher in publishers:
        publisher.authenticate()

    return publishers


def build_documentation(package, packages_path=tuple()):
    """Build all :ref:`rez_sphinx` registered documentation at ``directory``.

    Args:
        package (rez.packages.Package):
            The source Rez package to build documentation for.
        packages_path (list[str], optional):
            Paths on-disk to search within for an installed Rez package.  This
            package is assumed to have a defined `tests`_ attribute, containing
            a :ref:`rez_sphinx build` command. But if it doesn't exist, a
            default build command is used instead.

    Raises:
        NoDocumentationFound:
            If any found `tests`_ attributes ran, succeeded to run, but no
            destination documentation could be found.

    Returns:
        list[str]:
            The root directories on-disk where all documentation was generated
            into. For typical users, this list contains only one value.

    """

    def _to_exact_request(package):
        if not package.version:
            return package.name

        return "{package.name}=={package.version}".format(package=package)

    # TODO : This code assumes build_documentation exists. It may not. Make it optional!
    runner = package_test.PackageTestRunner(
        package_request=_to_exact_request(package),
        package_paths=packages_path,
    )
    tests = _validated_test_keys(runner)

    if not tests:
        root = finder.get_package_root(package)
        built_documentation = runner_.build(root)

        return [built_documentation]

    _LOGGER.info('Found "%s" documentation tests.', tests)

    output = []
    invalids = set()

    for name in tests:
        _LOGGER.info('Now building documentation with "%s".', name)

        result = runner.run_test(name)

        if result != _SUCCESS_EXIT_CODE:
            invalids.add(name)

            continue

        destination = _get_documentation_destination(name, package)

        if not destination:
            invalids.add(name)

        output.append(destination)

    if len(invalids) > 1:
        raise exception.NoDocumentationFound(
            "No documentation could be found after "
            '"{invalids}" commands were ran.'.format(
                invalids=", ".join(sorted(invalids))
            )
        )

    if invalids:
        raise exception.NoDocumentationFound(
            "No documentation could be found after "
            '"{invalids}" command was ran.'.format(invalids=next(iter(invalids)))
        )

    return output
