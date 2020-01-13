#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Find Python dependencies of other Python files and use that to get intersphinx data."""

import json
import logging
import os
import subprocess
import sys
import tempfile

from python_compatibility import import_parser, imports, packaging
from rez import packages_, resolved_context
from rez.config import config
from rez_utilities import inspection, url_help

_LOGGER = logging.getLogger(__name__)
_EXEMPTED = frozenset(("six",))


def _get_linked_rez_packages(items, excluded=None):
    """Get every Rez package for every file / folder in `items`.

    Args:
        items (iter[str]):
            The file or folder to search for Python files. Every Rez
            package that is imported through any of the Python files
            found in these locations will be returned.
        excluded (set[str], optional):
            Any found Rez package name found in this collection will not
            be returned. Default is None.

    Returns:
        set[:class:`rez.developer_package.DeveloperPackage`]:
            Get every dependency from every folder in `items`.

    """
    if not excluded:
        excluded = set()

    namespaces = set()

    for item in items:
        for path in packaging.iter_python_files(item):
            _LOGGER.debug('Processing "%s" Python file.', path)
            namespaces.update(
                (module.get_namespace() for module in import_parser.get_namespaces_from_file(path))
            )

    packages = dict()

    for namespace in namespaces:
        dependency = _get_rez_package_from_namespace(namespace)

        if not dependency:
            _LOGGER.warning(
                'Namespace "%s" does not come from a Rez package.', namespace
            )

            continue

        if dependency.name in excluded:
            # It's very common for a Python package to import parts of
            # its own modules so we ignore those imports here by adding
            # the caller package to `excluded`.
            #
            continue

        if dependency.name not in packages:
            packages[dependency.name] = dependency
        elif dependency.version > packages[dependency.name].version:
            # In practice, this will probably never happen. But, just in case.
            packages[dependency.name] = dependency

    return set(packages.values())


def _get_rez_package_from_namespace(namespace):
    """Get the Rez package from a Python dotted `namespace`.

    Args:
        namespace (str): A dotted Python string, such as "foo.bar" or ".foo.bar".

    Raises:
        RuntimeError: If the found module for `namespace` has no file path.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or NoneType:
            The found Rez package, if any.

    """
    module = imports.get_parent_module(namespace)

    if not module:
        _LOGGER.warning('Namespace "%s" is not importable.', namespace)

        return None

    try:
        path = module.__file__
    except AttributeError:
        if module.__name__ not in sys.builtin_module_names:
            for pattern in _EXEMPTED:
                if module.__name__.startswith(pattern.rstrip(".") + "."):
                    return None

            raise RuntimeError(
                'Module "{module}" has no file path but it is not a built-in module.'.format(
                    module=module
                )
            )

        return None

    return inspection.get_nearest_rez_package(path)


def get_intersphinx_links_from_requirements(requirements, allow_non_api=False):
    """Convert a Rez package's list of requirements into API documentation links.

    Args:
        requirements (iter[:class:`rez.utils.formatting.PackageRequest`]):
            The Package + version (if there is a version) information
            that will be used to query documentation details.
        allow_non_api (bool, optional):
            If False, only "recognized" API documentation will be
            returned. If True, all types of Rez documentation will be
            searched. Basically, False "guesses" correct documentation.
            Default is False.

    Returns:
        dict[str, tuple[str, None]]:
            Get every Rez package and its URL help documentation, if found.

    """
    packages = set()

    for requirement in requirements:
        package = packages_.get_latest_package(
            requirement.name, range_=requirement.range_
        )

        if package:
            packages.add(package)

            continue

        _LOGGER.warning('No Rez package was found for requirement "%s".', requirement)

    output = dict()

    finders = [url_help.find_api_documentation]

    if allow_non_api:
        finders.append(url_help.find_package_documentation)

    for package in packages:
        for finder in finders:
            documentation = finder(package)

            if documentation:
                output[package.name] = (documentation, None)

                break

    return output


def get_intersphinx_links_using_current_environment(name, items):
    """Create an intersphinx mapping for every dependency of a Rez package.

    Reference:
        https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

    Args:
        name (str):
            The Rez package which presumably is the root of every folder
            in `items`.
        items (iter[str]):
            The file or folder to search for Python files. Every Rez
            package that is imported through any of the Python files
            found in these locations will be returned.

    Returns:
        dict[str, tuple[str, None]]:
            Get every Rez package and its URL help documentation, if found.

    """
    packages = _get_linked_rez_packages(items, excluded={name})
    urls = dict()

    for package_ in packages:
        url = url_help.find_api_documentation(package_)

        if url:
            urls[package_.name] = (url, None)

    return urls


def get_intersphinx_links_from_rez_environment(
    package, items, add_rez_requirements=False, allow_non_api=False
):
    """Find intersphinx documentation URL links from a temporary Rez context.

    Generally, it's faster and more reliable to use
    :func:`get_intersphinx_links_using_current_environment`.
    But that function can only be used when your package +
    rez_documentation_check are both in the same resolve. (Which is
    rarely ever the case). This function creates a resolve context
    automatically for you and writes the intersphinx data, as a dict.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage` or NoneType):
            The Rez package that will be included along with
            rez_documentation_check into a single Rez context.
        items (iter[str]):
            The file or folder to search for Python files. Every Rez
            package that is imported through any of the Python files
            found in these locations will be returned.
        add_rez_requirements (bool, optional):
            If False, only Python imported modules will be used to
            search for documentation. If True, this function will also
            include all Rez packages in a user's ``requires`` attribute
            for documentation. Default is False.
        allow_non_api (bool, optional):
            If False, only "recognized" API documentation will be
            returned. If True, all types of Rez documentation will be
            searched. Basically, False "guesses" correct documentation.
            Default is False.

    Raises:
        RuntimeError:
            If ``rez-documentation-check find-intersphinx`` fails to
            run in the temporary Rez context or if the command fails to
            write a valid dict.

    Returns:
        dict[str, str or tuple[str, None]]: The found intersphinx mapping.

    """

    def _get_version(version):
        return tuple(
            [int(item) if item.isdigit() else item for item in str(version).split(".")]
        )

    this_version = os.environ["REZ_REZ_DOCUMENTATION_CHECK_VERSION"]

    if package.name == "rez_documentation_check" and _get_version(
        package.version
    ) > _get_version(this_version):
        packages = [
            "rez_documentation_check=={this_version}".format(this_version=this_version)
        ]
    else:
        packages = [
            "{package.name}=={package.version}".format(package=package),
            "rez_documentation_check=={this_version}".format(this_version=this_version),
        ]

    context = resolved_context.ResolvedContext(
        packages,
        package_paths=[inspection.get_packages_path_from_package(package)]
        + config.packages_path,  # pylint: disable=no-member
    )
    json_file = tempfile.NamedTemporaryFile(suffix=".json").name
    command = (
        'rez-documentation-check find-intersphinx "{package.name}" {items} '
        '--output "{json_file}"'.format(
            package=package,
            json_file=json_file,
            items=" ".join('"{item}"'.format(item=item) for item in items),
        )
    )

    if add_rez_requirements:
        command += " --add-rez-requirements"

    if allow_non_api:
        command += " --non-api"

    process = context.execute_shell(
        command=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, stderr = process.communicate()

    if stderr:
        _LOGGER.error(
            'Command "%s" failed to run. No intersphinx information could be found.',
            command,
        )
        raise RuntimeError(stderr)

    known_exceptions = (
        # Passing in a non-string type to `json.load`
        TypeError,
        # JSON syntax error
        ValueError,
    )

    with open(json_file, "r") as handler:
        try:
            return json.load(handler)
        except known_exceptions:
            raise RuntimeError(
                'Command "{command}" ran successfully but the output "{output}" '
                "is not a valid JSON dictionary. This should not happen and "
                "is an indication that ``rez-documentation-check`` API was changed."
                "".format(command=command, output=output)
            )
