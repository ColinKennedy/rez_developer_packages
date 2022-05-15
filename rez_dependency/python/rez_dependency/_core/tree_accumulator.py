"""Convert a Rez context into a dependency tree for further processing."""

from __future__ import print_function

import collections
import functools
import operator

from rez import packages

from . import exception


def _get_package(request, context):
    """Find an appropriate Rez package for ``request``.

    If ``request`` describes a runtime :ref:`requires`, it will use ``context``
    to get the resolved Rez package back. But if ``request`` is a build-related
    requirement, the best possible match is returned instead (since you won't
    necessarily find it in ``context``).

    Args:
        request (rez.utils.formatting.PackageRequest):
            A Rez package name + range to search within ``context`` or the
            greater :ref:`packages_path` environment.
        context (rez.resolved_context.ResolvedContext):
            A Rez context which contains basic runtime :ref:`requires`.

    Raises:
        NoPackage: If no package for ``request`` could be found.

    Returns:
        rez.packages.Package:
            The found package in ``context`` or the next best thing.

    """
    package = context.get_resolved_package(request.name)

    if package:
        # `request` is in the resolve, so it must've been somewhere in `requires`
        # or the initial package request.
        #
        return package

    # `request` was not in the resolve, so it may have been in `build_requires` or
    # `private_build_requires`. Either way, find it.

    try:
        return next(
            packages.iter_packages(
                request.name,
                range_=request.range,
                paths=context.package_paths,
            )
        )
    except StopIteration:
        raise exception.NoPackage(
            'Package "{request}" could not be found in '
            '"{context.package_paths}".'.format(
                request=request,
                context=context,
            )
        )


def _recurse_dependencies(dependency_query, node, context):
    """Describe **upstream** dependencies, ending at ``node``.

    Args:
        dependency_query (callable[rez.packages.Package] -> iter[rez.utils.formatting.PackageRequest]):  # pylint: disable=line-too-long
            Given a Rez package, get its dependencies.
        node (rez.utils.formatting.PackageRequest):
            A Rez package name + range to search within ``context`` or the
            greater :ref:`packages_path` environment.
        context (rez.resolved_context.ResolvedContext):
            A Rez context which contains basic runtime :ref:`requires`.

    Returns:
        dict[str, dict[str, ...]]: A recursive tree of upstream dependencies.

    """
    output = {}

    package = _get_package(node, context)

    for request in dependency_query(package):
        if request.ephemeral:
            # request == ".some_ephemeral-1"
            continue

        if request.conflict:
            # request == "!some_excludeded_package-1.1+<2"
            continue

        output[request.name] = _recurse_dependencies(dependency_query, request, context)

    return output


def _query_from(callers):
    """Create a wrapper function that uses ``callers`` to get dependencies of a package.

    Args:
        callers (list[callable[rez.packages.Package] -> iter[rez.utils.formatting.PackageRequest]]):  # pylint: disable=line-too-long
            Every function that, when called, returns some package dependencies.

    Returns:
        callable[rez.packages.Package] -> iter[rez.utils.formatting.PackageRequest]]:
            The wrapped function that yields a flat list of dependencies.

    """

    @functools.wraps(_query_from)
    def wrapped(package):
        for caller in callers:
            for request in caller(package) or []:
                yield request

        if hasattr(package, "variant_requires"):
            for request in package.variant_requires or []:
                yield request

    return wrapped


def collect_tree(context, query_using=tuple()):
    """Re-structure ``context``'s requested packages as a tree of **upstream** dependencies.

    Args:
        context (rez.resolved_context.ResolvedContext):
            A Rez context which contains basic runtime :ref:`requires`.
        query_using (list[callable[rez.packages.Package] -> iter[rez.utils.formatting.PackageRequest]], optional):  # pylint: disable=line-too-long
            Every function that, when called, returns some package dependencies.

    Returns:
        dict[str, dict[str, ...]]: A recursive tree of upstream dependencies.

    """
    if not query_using:
        query_using = [get_attribute_getter("requires")]

    query_from = _query_from(query_using)
    accumulation = collections.defaultdict(dict)

    for request in context.requested_packages():
        if request.ephemeral:
            # request == ".some_ephemeral-1"
            continue

        if request.conflict:
            # request == "!some_excludeded_package-1.1+<2"
            continue

        accumulation[request.name] = _recurse_dependencies(query_from, request, context)

    return accumulation


def get_attribute_getter(attribute):
    """callable[rez.packages.Package] -> iter[rez.utils.formatting.PackageRequest]: Wrap ``attribute`` into a caller."""  # pylint: disable=line-too-long
    return operator.attrgetter(attribute)
