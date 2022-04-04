"""The module which handles the :ref:`rez_sphinx publish run` command."""

import logging
import shlex

import six
from rez import package_test

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
        # TODO : Deal with this recursive import, later
        from .. import cli

        command = shlex.split(text)[1:]
        namespace = cli.parse_arguments(command)

        documentation_source = runner_.get_documentation_source(namespace.directory)
        documentation_build = runner_.get_documentation_build(documentation_source)

        return documentation_build

    test = package.tests[name]

    if isinstance(test, six.string_types):
        return _parse_destination(test)

    return _parse_destination(test[_REZ_TEST_COMMAND_KEY])


def _validated_test_keys(runner):
    """Get every :ref:`rez_sphinx`-registered `tests`_ key in ``runner``.

    Since :ref:`rez_sphinx.build_documentation_key` may be multiple values, we
    must check and return every matching key in ``runner``.

    Args:
        runner (rez.package_test.PackageTestRunner): The Rez package to query from.

    Raises:
        BadPackage:
            If ``runner`` has no tests or the defined tests have nothing in
            common with :ref:`rez_sphinx.build_documentation_key`.

    Returns:
        list[str]:
            Every found, matching key. In most cases, this will return either
            ``["build_documentation"]``, which is the default
            :ref:`rez_sphinx.build_documentation_key`, or nothing.

    """
    tests = runner.get_test_names()

    if not tests:
        raise exception.BadPackage(
            'Package "{package}" has no ``tests`` attribute.'.format(
                package=runner.get_package(),
            )
        )

    # TODO : It may make more sense to add a
    # `preference.get_publish_documentation_keys` and have that list default to
    # `preference.get_build_documentation_keys` if it is not defined. That way
    # users can specify publish keys differently than build ones.
    #
    build_tests = preference.get_build_documentation_keys()
    names = [name for name in build_tests if name in tests]

    if names:
        return names

    name = runner.get_package().name

    raise exception.BadPackage(
        'Package "{name}" has no rez_sphinx key for building documentation. '
        "Run ``rez_sphinx init`` to fix this.".format(name=name)
    )


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


def build_documentation(package):
    """Build all :ref:`rez_sphinx` registered documentation at ``directory``.

    Args:
        package (rez.packages.Package):
            The source Rez package to build documentation for.

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
    )
    tests = _validated_test_keys(runner)

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
