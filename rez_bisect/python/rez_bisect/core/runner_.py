#!/usr/bin/env python

"""The module which bisects Rez contexts to determine where an issue was introduced."""
# TODO : clean up this module later

from __future__ import division

import collections
import functools
import math
import random
import subprocess

from rez import resolved_context

from . import check


_NEWER = "newer_packages"
_REMOVED = "removed_packages"
_SUPPORTED_KEYS = frozenset((_NEWER, _REMOVED))


def _get_required_bad_packages(bad, diff, command):
    # """Get every Rez package name that contributes to some "bad" resolve.
    #
    # This function may return a list of only one Rez package name. But
    # it is also possible to return a 2-way, 3-way, or n-way Rez package issue.
    #
    # Args:
    #     bad (:class:`rez.resolved_context.ResolvedContext`):
    #         The context which fails to run `command`.
    #     diff (dict[str, list[:class:`rez.utils.formatting.PackageRequest`]]):
    #         Each type of Rez package (added, newer, older, removed, etc)
    #         and each version found between `bad` and a working, good resolve.
    #     command (str):
    #         The path to a shell script which, when run, will pass or succeed.
    #
    # Returns:
    #     list[:class:`rez.packages.Package`]:
    #         Each found package which contributes to the bad resolve.
    #
    # """
    _validate_keys(diff)

    newer_packages = diff.get(_NEWER)
    all_newer_packages = set(newer_packages.keys())
    # TODO : XXX Simplify this code, here
    tester = functools.partial(_get_testing_packages, bad, newer_packages)

    to_test = all_newer_packages
    # TODO : Add this optimization, if it actually makes bisecting faster, later
    # to_test = _get_candidate_packages(tester, all_newer_packages, command)
    required_packages = _get_required_bad_package_names(tester, to_test, command)

    return {name: newer_packages[name] for name in required_packages}


# TODO : Simplify these parameters, if possible
def _get_partial_context(good, diff, command):
    """Check all Rez package at once to find a close-ish match that fails `command`.

    The objective of this is not to get a perfect context which shows
    exactly when `command` begins to fail. The objective is to get close
    enough so other functions can begin finessing to find the best
    context.

    For a more exact match, see :func:`_get_required_bad_packages`.

    Args:
        good (:class:`rez.resolved_context.ResolvedContext`):
            The context which will pass if we run `command` within it.
        diff (dict[str, list[:class:`rez.utils.formatting.PackageRequest`]]):
            Each type of Rez package (added, newer, older, removed, etc)
            and each version found between `good` and a failing resolve.
        command (str):
            The path to a shell script which, when run, will pass or succeed.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The context which determines the exact context where
            `command` starts failing.

    """

    def _newer_indices_to_context(newer_indices):
        closest_newer = {key: value + 1 for key, value in newer_indices.items()}
        request = [newer_packages[key][index] for key, index in closest_newer.items()]

        return resolved_context.ResolvedContext(
            _to_request(request),
            package_paths=good.package_paths,
        )

    _validate_keys(diff)

    previous_weight = 1
    weight = 0.5
    newer_packages = diff.get(_NEWER)
    newer = newer_packages.values()
    previous = None

    while True:
        newer_indices = dict()
        request = []

        for packages in newer:
            index = math.floor(len(packages) * weight)
            package = packages[index]

            request.append(package)
            newer_indices[package.name] = index

        checker_context = resolved_context.ResolvedContext(
            _to_request(request),
            package_paths=good.package_paths,
        )

        average = (weight + previous_weight) / 2
        offset = abs(average - weight)

        if not check.is_good(checker_context, command):
            previous_weight = weight
            weight = weight - offset

            continue

        # TODO : Check why this is producing a redundant check. Make it more efficient
        if request == previous:
            break

        previous_weight = weight
        weight += offset
        previous = request

    return _newer_indices_to_context(newer_indices)


def _get_candidate_packages(tester, all_newer_packages, command):
    """Find every Rez package needed to create a "good" resolve.

    Args:
        tester (callable[set[str]] -> :class:`rez.resolved_context.ResolvedContext`):
            A function which takes Rez packages names and returns
            a context which includes a resolve containing those
            names. This function usually contains a "bad" resolve and
            each Rez package name will test more "good" Rez packages /
            versions. In other words, the more packages passed to this
            function, the more likely the context which it returns will
            be "good".
        all_newer_packages (set[str]):
            The Rez packages which contribute to a "good" resolve.
        command (str):
            A script used to determine if more or less packages are
            needed from `all_newer_packages`.

    Returns:
        set[str]:
            Every Rez package name which may or may not contribute to a
            "bad" resolve.

    """
    to_test = set(_get_half_randomly(all_newer_packages))

    while True:
        context = tester(to_test)

        if check.is_good(context, command):
            # `to_test` contains enough packages that it turns `bad`
            # into a good resolve again. So we're done
            break

        # We didn't include enough packages. Expand the number of
        # packages which we will test and re-try.
        #
        to_test.update(_get_half_randomly(all_newer_packages - to_test))

    return to_test


def _get_combined_context(good, bad_packages):
    bad_packages_data = {package.name: package for package in bad_packages}
    requested_names = {request.name for request in good.requested_packages()}
    packages = []

    for variant in good.requested_packages():
        if variant.name not in requested_names:
            continue

        try:
            package = bad_packages_data[variant.name]
        except KeyError:
            package = good.get_resolved_package(variant.name)

        packages.append(package)

    context = resolved_context.ResolvedContext(
        _to_request(packages),
        package_paths=good.package_paths,
    )

    return context


# def _get_full_context(good, diff, command):
#     # Choose one
#     # - Partial context it
#     # - save that result and incorporate it into a new test
#     # Choose another
#     # - repeat
#     # Continue until all packages have had versions chosen
#
#     def _choose_one(packages):
#         return random.sample(packages, 1)[0]
#
#     checked = set()
#     bads = set()
#     newer = diff.get(_NEWER)
#
#     while True:
#         candidates = set(newer.keys()) - checked - bads
#
#         if not candidates:
#             break
#
#         chosen = _choose_one(candidates)
#         diff_with_chosen = _make_diff_from_packages([chosen], diff)
#         context = _get_partial_context(good, diff_with_chosen, command)
#
#         if check.is_good(context, command):
#             checked.add(chosen)
#
#             continue
#
#         bads.add(chosen)
#
#     # def _half_diff(diff, exclude):
#     #     output = dict()
#     #
#     #     for key, data in diff.items():
#     #         halved_data_keys = _get_half_randomly(set(data.keys()) - exclude)
#     #
#     #         if not halved_data_keys:
#     #             continue
#     #
#     #         output.setdefault(key, dict())
#     #         output[key].update(
#     #             {key: value for key, value in data.items() if key in halved_data_keys}
#     #         )
#     #
#     #     return output
#     #
#     # original_bad_packages = set()
#     # bad_names = set()
#     #
#     # for data in diff.values():
#     #     for name, packages in data.items():
#     #         bad_names.add(name)
#     #         package = packages[-1]
#     #         original_bad_packages.add((package.name, package.version))
#     #
#     # safe_packages = set()
#     #
#     # while True:
#     #     half_diff = _half_diff(diff, safe_packages)
#     #
#     #     if not half_diff:
#     #         # There is nothing more to check
#     #         raise ValueError(safe_packages)
#     #         break
#     #
#     #     context = _get_partial_context(good, half_diff, command)
#     #
#     #     for name in bad_names:
#     #         bad_package = context.get_resolved_package(name)
#     #
#     #         if (bad_package.name, bad_package.version) in original_bad_packages:
#     #             safe_packages.add(bad_package.name)


def _get_exact_versions(bad, diff, bad_packages, command):
    # TODO : This function is unoptimized. It checks packages by-name,
    # one at a time, to get the exact version that it needs.  We should
    # do a binary walk or group the packages together at once, so we
    # don't just walk each package one at a time.
    #
    # It also only advances through each version, one at a time. It's very unoptimized
    #
    package_names = set(bad_packages.keys())
    output = set()

    for name in package_names:
        check_diff = _make_diff_from_packages({name}, diff)
        newer = check_diff.get(_NEWER, dict())

        for packages in newer.values():
            previous = None

            for package in reversed(packages):
                context = _get_combined_context(bad, {package})

                if not check.is_good(context, command):
                    previous = package
                else:
                    output.add(previous)

                    break

    return output


def _get_full_context(good, bad_packages):
    """Get a Rez context that exactly replaces some issue, using `bad_packages`.

    Args:
        good (:class:`rez.resolved_context.ResolvedContext`):
            A context which does not have an issue. This resolve is used
            as a reference and `bad_packages` are added into it in order
            to "make it turn bad".
        bad_packages (iter[:class:`rez.packages.Package`]):
            All Rez packages whose versions contribute to an issue.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The generated context which contains the exact Rez packages
            + versions which caused some kind of issue.

    """
    bad_packages_data = {package.name: package for package in bad_packages}

    packages = []

    for variant in good.requested_packages():
        try:
            package = bad_packages_data[variant.name]
        except KeyError:
            package = good.get_resolved_package(variant.name)

        packages.append(package)

    context = resolved_context.ResolvedContext(
        _to_request(packages),
        package_paths=good.package_paths,
    )

    return context


def _get_half_randomly(items):
    """Get half of all given `items`."""
    if len(items) == 1:
        return list(items)

    return random.sample(items, (len(items) // 2))


def _get_required_bad_package_names(tester, all_candidates, command):
    to_test = set(all_candidates)
    checked = set()

    while True:
        first = set(_get_half_randomly(to_test))
        context = tester(first)

        if not check.is_good(context, command):
            raise NotImplementedError("Im bad")

            break


        if to_test == first:
            return checked.union(first)

        loop_test = to_test - first
        context = tester(loop_test)

        if not check.is_good(context, command):
            raise NotImplementedError(
                'This should never happen. Fix! "{to_test} {first}"'.format(
                    to_test=to_test, first=first
                )
            )

        checked.update(to_test - loop_test)
        to_test = loop_test

    raise NotImplementedError("Figure out what to do, here.")


def _get_testing_packages(bad, newer_packages, good_selection):
    """Create a context which is a combination of `bad` and `newer_packages`.

    Args:
        bad (:class:`rez.resolved_context.ResolvedContext`):
            The context which has an issue.
        newer_packages (dict[str, list[:class:`rez.packages.Package` or :class:`rez.packages.Variant`]]):
            All package & versions which make up a good and bad resolve.
            The 0th index should always be a Rez package version which
            can create a "good" resolve.
        good_selection (iter[str]):
            The Rez packages to pick for the new context. If included,
            the "good" version of the package from `newer_packages` is
            used. Otherwise, whatever package version from `bad` will
            remain.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The merged context containing `bad` and the good package
            version from `good_selection`.

    """
    # 1. `packages` is initially filled with only packages which
    # contribute to a "bad" resolve and not to any "good" resolve. This
    # will change shortly (see below).
    #
    # TODO : Check if you can use requested packages, instead
    packages = {variant.name: variant for variant in bad.resolved_packages}

    for name in good_selection:
        a_working_package = newer_packages[name][0]
        packages[name] = a_working_package

    # 2. By this point, `packages` should be a mix of package name-variants
    # which create a "bad" resolve. But `good_selection` should include
    # a few packages which actually contribute to a "good" resolve.
    #
    return resolved_context.ResolvedContext(
        _to_request(packages.values()),
        package_paths=bad.package_paths,
    )


def _make_diff_from_packages(names, reference_diff):
    """Filter `reference_diff` with the Rez package `names`.

    Args:
        names (set[str]):
            Each Rez package name to filter by. Only variants / packages
            in `reference_diff` which match a name in this parameter
            will be returned.
        reference_diff (dict[str, dict[str, list] or list]):
            The Rez diff (usually generated using
            :meth:`rez.resolved_context.ResolvedContext.get_resolve_diff`)
            to filter by.

    Returns:
        dict[str, dict[str, list] or list]: The filtered diff.

    """
    output = dict()

    for key, data in reference_diff.items():
        if isinstance(data, collections.MutableMapping):
            data = {name: packages for name, packages in data.items() if name in names}
        else:
            data = [package for package in data if package.name in names]

        if data:
            output[key] = data

    return output


def _to_request(request):
    """Convert Rez packages / variants into something Rez contexts can use.

    Todo:
        Check if this is needed.

    Args:
        request (iter[:class:`rez.packages.Package` or :class:`rez.packages.Variant`]):
            The installed package name-version to convert.

    Returns:
        list[str]: A request which can be sent to a Rez context.

    """
    return [
        "{package.name}=={package.version}".format(package=package)
        for package in request
    ]


def _validate_keys(diff):
    """Make sure `diff` can be processed by functions in this module.

    Todo:
        Check if this function is actually needed

    Args:
        diff (dict[str, object]): The Rez diff to check.

    Raises:
        RuntimeError: If `diff` has any keys which we do not know how to process.

    """
    keys = set(diff.keys())
    unsupported = keys - _SUPPORTED_KEYS

    if unsupported:
        raise RuntimeError(
            'Unknown keys "{unsupported}" were found. Expected "{_SUPPORTED_KEYS}".'.format(
                unsupported=unsupported, _SUPPORTED_KEYS=_SUPPORTED_KEYS
            )
        )


def bisect(good, bad, command):
    """Find the closest resolve between two Rez resolves which fails `command`.

    Args:
        good (:class:`rez.resolved_context.ResolvedContext`): The context
            which succeeds in running `command`.
        bad (:class:`rez.resolved_context.ResolvedContext`): The context
            which fails to run `command`.
        command (str): The path
            to a shell script which, when run, will pass or succeed.

    """
    # partial_context = _get_partial_context(good, good.get_resolve_diff(bad), command)
    #
    # bad_packages = _get_required_bad_packages(
    #     partial_context, good.get_resolve_diff(partial_context), command
    # )
    #
    # # `minimum_bad_context` contains all good packages + each Rez
    # # package (`bad_packages`) which contributes to `command` failing.
    # #
    # minimum_bad_context = _get_combined_context(good, bad_packages)
    #
    # return _get_full_context(good, good.get_resolve_diff(minimum_bad_context), command)

    def _filter_requests(diff, contexts):
        request = {package.name for context in contexts for package in context.requested_packages()}

        return _make_diff_from_packages(request, diff)

    def _get_request_diff(left, right):
        return _filter_requests(left.get_resolve_diff(right), [left, right])

    partial_context = _get_partial_context(
        good,
        _get_request_diff(good, bad),
        command,
    )

    reduced_diff = _get_request_diff(good, partial_context)

    all_bad_packages = _get_required_bad_packages(
        partial_context, reduced_diff, command
    )

    bad_packages = _get_exact_versions(bad, reduced_diff, all_bad_packages, command)

    return _get_full_context(good, bad_packages)

    # bad_packages = _get_required_bad_packages(
    #     partial_context, good.get_resolve_diff(partial_context), command
    # )
    #
    # # `minimum_bad_context` contains all good packages + each Rez
    # # package (`bad_packages`) which contributes to `command` failing.
    # #
    # minimum_bad_context = _get_combined_context(good, bad_packages)
    #
    # return _get_full_context(good, good.get_resolve_diff(minimum_bad_context), command)


def summarize(good, bad):
    """Explain what in `bad` caused `good` to not work.

    Args:
        good (:class:`rez.resolved_context.ResolvedContext`):
            A resolve which doesn't have any command issues.
        bad (:class:`rez.resolved_context.ResolvedContext`):
            A minimal resolve, based on `good`, that has 1-or-more Rez
            packages which cause some kind of "bad-ness" or issue.

    Returns:
        dict[str, set[:class:`rez.packages.Package`]]:
            Each found, bad package and the section it is a part of.

    """
    output = dict()

    for key, data in good.get_resolve_diff(bad).items():
        if not hasattr(data, "values"):
            output[key] = data

            continue

        output.setdefault(key, set())

        for packages in data.values():
            output[key].add(packages[-1])

    return output
