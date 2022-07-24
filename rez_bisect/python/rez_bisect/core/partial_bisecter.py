"""A companion for :mod:`.runner` to make bisecting easier.

Most of the functions here are heuristics (guesses) to find the exact Rez
package(s) that cause some issue. For example, :func:`bisect_2d`. However
there's no guarantee that the found diff is 100% accurate. It's just to give
the user a reasonable guess.

"""

import collections
import functools
import itertools
import logging
import math
import random

from rez import resolved_context

from . import diff_mate

_ADDED = "added_packages"
_NEWER = "newer_packages"
_OLDER = "older_packages"
_REMOVED = "removed_packages"
_SUPPORTED_KEYS = frozenset((_ADDED, _NEWER, _OLDER, _REMOVED))

_NudgeResults = collections.namedtuple(
    "_NudgeResults",
    [
        "older",
        "newer",
        "removed",
        "older_indices",
        "newer_indices",
        "removed_packages",
    ],
)

_LOGGER = logging.getLogger(__name__)


def _check_by_type_is_bad(has_issue, good, diff, key, exclude=False):
    bad_packages = _get_bad_package_request(diff, key)

    if not bad_packages:
        return []

    context = _get_quick_context(good, bad_packages, exclude=exclude)

    if has_issue(context):
        return bad_packages

    return []


def _check_removed_is_bad(has_issue, good, diff, key):
    bad_packages = _get_bad_package_request(diff, key)

    if not bad_packages:
        return []

    bad_request_names = {request.name for request in bad_packages}
    requested_good_packages = []

    for request in good.requested_packages():
        if request.name not in bad_request_names:
            requested_good_packages.append(request)

    context = resolved_context.ResolvedContext(
        requested_good_packages,
        package_paths=good.package_paths,
    )

    if has_issue(context):
        return bad_packages

    return []


def _get_approximate_bisect(has_issue, good, diff):
    """Check all Rez packages at once to find a close-ish match, based on ``diff``.

    The objective of this function is do give an approximate bisect. The result
    can then be handed off to other, more granular functions can finess and
    find a more accurate bisect result.

    For a more exact bisect, see :func:`_get_exact_bisect`.

    Note:
        This function is more efficient if you use a diff of Rez package
        requests, not a diff of the resolved Rez packages.

    Args:
        has_issue (callable[rez.resolved_context.Context] -> bool):
            A function that returns True if the executable ``path`` fails.
            Otherwise, it returns False, indicating success. It takes a Rez
            :ref:`context` as input.
        good (rez.resolved_context.ResolvedContext):
            The context which would return False for ``has_issue(good)``.
            It's the last context before some issue begins occurring.
        diff (dict[str, list[rez.utils.formatting.PackageRequest]]):
            Each type of Rez package (added, newer, older, removed, etc) and
            each version found between ``good`` and another failing resolve.

    Returns:
        rez.resolved_context.ResolvedContext:
            The context which determines the an approximate context where
            ``has_issue`` starts failing.

    """

    def _get_next_change_request(indices, reference_diff):
        output = []

        for key, index in indices.items():
            next_index = index + 1
            candidates = reference_diff[key]

            if next_index >= len(candidates):
                # This usually occurs whenever ``indices`` represents some diff
                # which actually **doesn't** contribute to ``has_issue``. That
                # means we can safely ignore it.
                #
                # TODO : Add lots of unittests to ensure this assumption is okay.
                #
                _LOGGER.debug('Skipping "%s" candidates.', candidates)

                continue

            output.append(candidates[next_index])

        return output

    _validate_keys(diff)

    # 1. Check to see if only the added packages cause something bad to occur
    # 1a. Check if removed packages cause the issue.
    #
    # # TODO : Make this work, later
    # does_not_has_issue = _invert(has_issue)
    # bad_removed = _check_by_type_is_bad(does_not_has_issue, good, diff, _REMOVED)
    #
    # if bad_removed and has_issue():
    #     return {_REMOVED: bad_removed}

    # 1c. Check if added packages cause the issue.
    bad_added = _check_by_type_is_bad(has_issue, good, diff, _ADDED)

    if bad_added:
        return {_ADDED: bad_added}

    # 2. If we got this far, it's because a combination of packages is likely
    # the problem. We now "nudge" the packages to get as close to the problem
    # as possible and return it.
    #
    results = _get_nudged_packages(has_issue, good, diff)

    output = {}

    bad_newer = _get_next_change_request(results.newer_indices, results.newer)

    if bad_newer:
        output[_NEWER] = bad_newer

    bad_older = _get_next_change_request(results.older_indices, results.older)

    if bad_older:
        output[_OLDER] = bad_older

    bad_removed = results.removed_packages

    if bad_removed:
        output[_REMOVED] = bad_removed

    return output


def _get_bad_package_request(diff, key):
    names = diff.get(key) or []

    if not hasattr(names, "values"):
        names = [package.name for package in names]

    sequence_diff = diff_mate.get_request_diff(names, diff)

    if key not in sequence_diff:
        return set()

    value = sequence_diff[key]

    if not hasattr(value, "values"):
        return value

    # TODO : Finish
    raise ValueError(value)

    return {
        list(packages)[-1]
        for packages in value.values() or []
    }


def _get_nudged_packages(has_issue, good, diff):

    def _get_from_change_dict(weight, packages):
        request = []
        output = {}

        for name, versions in packages.items():
            index = math.floor(len(versions) * weight)
            package = versions[index]

            request.append(package)
            output[package.name] = index

        return output, request

    def _get_from_change_list(weight, packages, good):
        request = []
        output = {}

        max_index = math.floor(len(packages) * weight)

        for package in packages[:max_index]:
            output.add(package.name)

        requested = good.requested_packages()

        for package in packages[max_index:]:
            found = [package_ for package_ in requested if package_.name == package.name]
            request.extend(found)

        return output, request

    previous_weight = 1
    weight = 0.5
    older = diff.get(_OLDER) or {}
    newer = diff.get(_NEWER) or {}
    removed = diff.get(_REMOVED) or []
    previous = None

    while True:
        request = []

        newer_indices, extra = _get_from_change_dict(weight, newer)
        request.extend(extra)
        older_indices, extra = _get_from_change_dict(weight, older)
        request.extend(extra)
        removed_packages, remaining_requests = _get_from_change_list(weight, removed, good)
        raw_request = _to_raw_request(request)
        raw_request.extend(remaining_requests)

        context = resolved_context.ResolvedContext(
            raw_request,
            package_paths=good.package_paths,
        )

        average = (weight + previous_weight) / 2
        offset = abs(average - weight)

        if has_issue(context):
            # Since ``context`` still has an issue, we nudge ``weight`` to move
            # away from the bad ``diff`` and closer to ``good`` so the next
            # iteration of ``has_issue(context)`` has a greater chance of
            # returning False.
            #
            previous_weight = weight
            weight = weight - offset

            continue

        # TODO : Check why this is producing a redundant check. Make it more efficient
        if request == previous:
            break

        previous_weight = weight
        weight += offset
        previous = request

    return _NudgeResults(
        older,
        newer,
        removed,
        older_indices,
        newer_indices,
        remaining_requests,
    )


# def _get_ephemeral_diff(left, right):
#     left_families = {requirement.name: requirement for requirement in left.resolved_ephemerals}
#     right_families = {requirement.name: requirement for requirement in right.resolved_ephemerals}
#
#     added = set()
#     changed = set()
#     removed = set()
#
#     for requirement in left.resolved_ephemerals:
#         if requirement.name not in right_families:
#             removed.add(requirement)
#
#             continue
#
#         if requirement.range != right_families[requirement.name].range:
#             changed.add(requirement)
#
#     for requirement in right.resolved_ephemerals:
#         if requirement.name not in left_families:
#             added.add(requirement)
#
#     output = {}
#
#     if added:
#         output[_ADDED_EPHEMERALS] = added
#
#     if changed:
#         output[_CHANGED_EPHEMERALS] = changed
#
#     if removed:
#         output[_REMOVED_EPHEMERALS] = removed
#
#     return output


# TODO : Consider removing this function, `_get_exact_bisect`. If it becomes too simple
def _get_exact_bisect(has_issue, good, diff):
    # """Find the Rez package(s)/version(s) that cause ``good`` to become bad.
    #
    # The general workflow steps are:
    #
    # - Test each "change type" to find a likely error
    #
    #     - Likely scenarios such as:
    #
    #         - Adding a package causes some problem
    #         - Removing a package causes some problem
    #
    #     - If found, test individual components, to find "the bad one(s)"
    #
    # Args:
    #     has_issue (callable[rez.resolved_context.Context] -> bool):
    #         A function that returns True if the executable ``path`` fails.
    #         Otherwise, it returns False, indicating success. It takes a Rez
    #         :ref:`context` as input.
    #     good (rez.resolved_context.ResolvedContext):
    #         The context which would return False for ``has_issue(good)``.
    #         It's the last context before some issue begins occurring.
    #     diff (rez.resolved_context.Context):
    #         The earliest context that fails ``has_issue(bad)``.
    #
    # Returns:
    #     dict[str, list[rez.packages.Package]]:
    #         All found diff content that causes ``good`` to become ``bad`` and
    #         each package versions found, in between.
    #
    # """

    def _choose_one(packages):
        return random.sample(packages, 1)[0]

    required_bad = _check_by_type_is_bad(has_issue, good, diff, _ADDED)

    if required_bad:
        required_bad = _narrow_candidates(has_issue, good, required_bad)

        return {_ADDED: required_bad}

    required_bad = _check_by_type_is_bad(has_issue, good, diff, _REMOVED, exclude=True)

    if required_bad:
        required_bad = _narrow_candidates(has_issue, good, required_bad, exclude=True)

        return {_REMOVED: required_bad}

    required_bad = _check_by_type_is_bad(has_issue, good, diff, _NEWER)

    if required_bad:
        required_bad = _narrow_candidates(has_issue, good, required_bad)

        return {_NEWER: required_bad}

    required_bad = _check_by_type_is_bad(has_issue, good, diff, _OLDER)

    if required_bad:
        required_bad = _narrow_candidates(has_issue, good, required_bad)

        return {_OLDER: required_bad}

    raise NotImplementedError()


def _get_filtered_matches(diff, matches):
    output = {}

    for key, values in diff.items():
        if isinstance(values, collections.MutableMapping):
            new = {}

            for name, packages in values.items():
                inner = [package for package in packages for match in matches if match(package.name)]

                if inner:
                    new[name] = inner
        else:
            new = [item for item in values for match in matches if match(item.name)]

        if new:
            output[key] = new

    return output


def _get_filtered_request_diff(good, bad):
    """Make a diff using only the requested Rez packages.

    Rez's :meth:`rez.resolved_context.ResolvedContext.get_resolve_diff` is good
    but it returns the diff of every Rez package, even nested dependencies.
    This function only returns the diff of packages which were included in the
    user's original package request.

    Args:
        good (rez.resolved_context.ResolvedContext):
            The context which would return False for ``has_issue(good)``.
            It's the last context before some issue begins occurring.
        bad (rez.resolved_context.ResolvedContext):
            The earliest context that fails ``has_issue(bad)``.

    Returns:
        dict[str, list[rez.packages.Package]]: The simplified diff.

    """
    contexts = [good, bad]
    requests = {
        package.name for context in contexts for package in context.requested_packages()
    }
    resolve_diff = good.get_resolve_diff(bad)
    request_diff = diff_mate.get_request_diff(requests, resolve_diff)

    return {key: value for key, value in request_diff.items() if value}


def _get_quick_context(good, bad_request, exclude=False):
    # bad_request list[PackageRequest]
    bad_request_names = {request.name for request in bad_request}
    requested_good_packages = []

    for request in good.requested_packages():
        if request.name not in bad_request_names:
            requested_good_packages.append(request)

    request = requested_good_packages

    if not exclude:
        request += _to_raw_request(bad_request)

    return resolved_context.ResolvedContext(request, package_paths=good.package_paths)


def _invert(caller):
    @functools.wraps(caller)
    def wrapped(*args, **kwargs):
        return not caller(*args, **kwargs)

    return wrapped


def _narrow_candidates(has_issue, good, request, exclude=False):
    if not request:
        raise RuntimeError('Request cannot be empty.')

    count = 1
    length = len(request)

    while count <= length:
        for packages in itertools.combinations(request, count):
            context = _get_quick_context(good, packages, exclude=exclude)

            if has_issue(context):
                return packages

        count += 1

    raise RuntimeError('Request "{request}" could not be narrowed.'.format(request=request))


def _to_raw_request(request):
    """Convert Rez packages / variants into something Rez contexts can use.

    Todo:
        Check if this is needed.

    Args:
        request (
            iter[
                rez.packages.Package
                or rez.packages.Variant
                or rez.utils.formatting.PackageRequest
            ]
        ):
            The installed package name-version to convert.

    Raises:
        NotImplementedError:
            If ``request`` contains something that this function cannot process.

    Returns:
        list[str]: A request which can be sent to a Rez context.

    """
    output = []

    for item in request:
        if hasattr(item, "version"):
            output.append("{item.name}=={item.version}".format(item=item))
        elif hasattr(item, "range"):
            output.append(str(item))
        else:
            raise NotImplementedError('Item "{item}" cannot be processed.'.format(item=item))

    return output


# TODO : Remove this function later once everything is supported
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


def bisect_2d(has_issue, good, bad, matches=None):
    """Find the Rez package(s)/version(s) that cause ``good`` to become bad.

    How it works:

    - For all changes (newer packages, older packaged, added packages, removed packages)

        - Bisect between all changes to get roughly close enough

    - From the approximate bisect, narrow down to individual package(s)

    Args:
        has_issue (callable[rez.resolved_context.Context] -> bool):
            A function that returns True if the executable ``path`` fails.
            Otherwise, it returns False, indicating success. It takes a Rez
            :ref:`context` as input.
        good (rez.resolved_context.ResolvedContext):
            The context which would return False for ``has_issue(good)``.
            It's the last context before some issue begins occurring.
        bad (rez.resolved_context.Context):
            The earliest context that fails ``has_issue(bad)``.

    Returns:
        dict[str, list[rez.packages.Package]]:
            All found diff content that causes ``good`` to become ``bad`` and
            each package versions found, in between.

    """
    request_diff = _get_filtered_request_diff(good, bad)

    if matches:
        request_diff = _get_filtered_matches(request_diff, matches)

    unfinished_diff = _get_approximate_bisect(has_issue, good, request_diff)

    return _get_exact_bisect(has_issue, good, unfinished_diff)
