"""A companion for :mod:`.runner` to make bisecting easier.

Most of the functions here are heuristics (guesses) to find the exact Rez
package(s) that cause some issue. For example, :func:`bisect_2d`. However
there's no guarantee that the found diff is 100% accurate. It's just to give
the user a reasonable guess.

"""

import itertools
import math
import random

from rez import resolved_context

from . import diff_mate

_ADDED = "added_packages"
_NEWER = "newer_packages"
_OLDER = "older_packages"
_REMOVED = "removed_packages"
_SUPPORTED_KEYS = frozenset((_ADDED, _NEWER, _OLDER, _REMOVED))


def _get_approximate_bisect(has_issue, good, diff):
    """Check all Rez packages at once to find a close-ish match, based on ``diff``.

    The objective of this function is do give an approximate bisect. The result
    can then be handed off to other, more granular functions can finess and
    find a more accurate bisect result.

    For a more exact bisect, see :func:`_get_required_bad_packages`.

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

    def _get_from_change_list(sequence, request):
        output = {}

        for packages in sequence:
            index = math.floor(len(packages) * weight)
            package = packages[index]

            request.append(package)
            output[package.name] = index

        return output

    def _get_next_change_request(indices, reference_diff):
        closest = {key: value + 1 for key, value in indices.items()}

        return [reference_diff[key][index] for key, index in closest.items()]

    _validate_keys(diff)

    previous_weight = 1
    weight = 0.5
    older_packages = diff.get(_OLDER) or {}
    newer_packages = diff.get(_NEWER) or {}
    older = older_packages.values()
    newer = newer_packages.values()
    previous = None

    while True:
        request = []

        newer_indices = _get_from_change_list(newer, request)
        older_indices = _get_from_change_list(older, request)

        context = resolved_context.ResolvedContext(
            _to_raw_request(request),
            package_paths=good.package_paths,
        )

        average = (weight + previous_weight) / 2
        offset = abs(average - weight)

        if has_issue(context):
            # We nudge ``weight`` to move away from ``diff`` and closer to
            # ``good`` so the next iteration of ``has_issue(context)``
            # has a greater chance of returning False.
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

    request = []
    request.extend(_get_next_change_request(newer_indices, newer_packages))
    request.extend(_get_next_change_request(older_indices, older_packages))

    return resolved_context.ResolvedContext(
        _to_raw_request(request),
        package_paths=good.package_paths,
    )


def _get_required_bad_packages():
    # TODO : Make this real or delete it + all references to it
    raise ValueError()


def _to_raw_request(request):
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
        bad (rez.resolved_context.Context):
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


def _get_exact_bisect(has_issue, good, bad):
    """Find the Rez package(s)/version(s) that cause ``good`` to become bad.

    The general workflow steps are:

    - Test each "change type" to find a likely error

        - Likely scenarios such as:

            - Adding a package causes some problem
            - Removing a package causes some problem

        - If found, test individual components, to find "the one(s)"

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

    def _get_bad_package_request(diff, key):
        sequence_diff = diff_mate.get_request_diff(diff.get(key) or [], diff)

        if key not in sequence_diff:
            return set()

        return {
            list(packages)[-1]
            for packages in sequence_diff[key].values()
        }

    def _get_quick_context(good, bad_request):
        # raise ValueError(sorted(item for item in dir(good) if "" in item.lower()))
        bad_request_names = {request.name for request in bad_request}
        requested_good_packages = []

        for request in good.requested_packages():
            if request.name not in bad_request_names:
                requested_good_packages.append(request)

        return resolved_context.ResolvedContext(
            requested_good_packages + _to_raw_request(bad_request),
            package_paths=good.package_paths,
        )

    def _check_by_type_is_bad(good, diff, key):
        bad_packages = _get_bad_package_request(diff, key)

        if not bad_packages:
            return []

        if has_issue(_get_quick_context(good, bad_packages)):
            return bad_packages

        return []

    def _choose_one(packages):
        return random.sample(packages, 1)[0]

    def _narrow_candidates(has_issue, good, request):
        if not request:
            raise RuntimeError('Request cannot be empty.')

        count = 1
        length = len(request)

        while count <= length:
            for packages in itertools.combinations(request, count):
                context = _get_quick_context(good, packages)

                if has_issue(context):
                    return packages

            count += 1

        raise RuntimeError('Request "{request}" could not be narrowed.'.format(request=request))

    diff = _get_filtered_request_diff(good, bad)

    checked = set()
    bads = set()
    bad_packages = set()

    required_bad = _check_by_type_is_bad(good, diff, _NEWER)

    if required_bad:
        required_bad = _narrow_candidates(has_issue, good, required_bad)

        return {_NEWER: required_bad}

    required_bad = _check_by_type_is_bad(good, diff, _OLDER)

    if required_bad:
        required_bad = _narrow_candidates(has_issue, good, required_bad)

        return {_OLDER: required_bad}

    raise NotImplementedError()

    # while True:
    #     candidates = set(newer.keys()) - checked - bads
    #
    #     if not candidates:
    #         break
    #
    #     chosen = _choose_one(candidates)
    #     chosen_diff = diff_mate.get_request_diff([chosen], diff)
    #     context = _get_approximate_bisect(has_issue, good, chosen_diff)
    #
    #     if not has_issue(context):
    #         checked.add(chosen)
    #
    #         continue
    #
    #     bads.add(chosen)
    #     bad_packages.add(context.get_resolved_package(chosen))
    #
    # bad_package_map = {package.name: package for package in bad_packages}
    #
    # return diff_mate.filter_by_packages(bad_package_map, diff)


def bisect_2d(has_issue, good, bad):
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
    unfinished_context = _get_approximate_bisect(has_issue, good, request_diff)

    return _get_exact_bisect(has_issue, good, unfinished_context)
