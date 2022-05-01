import math
import random

from rez import resolved_context

from . import diff_mate

_NEWER = "newer_packages"
_REMOVED = "removed_packages"
_SUPPORTED_KEYS = frozenset((_NEWER, _REMOVED))


def _get_approximate_bisect(has_issue, good, diff):
    """Check all Rez packages at once to find a close-ish match, based on ``diff``.

    The objective of this function is do give an approximate bisect.  The
    result can then be handed off to other, more granular functions can finess
    and find a more accurate bisect result.

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

    def _newer_indices_to_context(newer_indices):
        closest_newer = {key: value + 1 for key, value in newer_indices.items()}
        request = [newer_packages[key][index] for key, index in closest_newer.items()]

        return resolved_context.ResolvedContext(
            _to_raw_request(request),
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

    return _newer_indices_to_context(newer_indices)


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
    requests = {package.name for context in contexts for package in context.requested_packages()}
    resolve_diff = good.get_resolve_diff(bad)
    request_diff = diff_mate.get_request_diff(requests, resolve_diff)

    return {key: value for key, value in request_diff.items() if value}


def _get_exact_bisect(has_issue, good, bad):
    """Find the Rez package(s)/version(s) that cause ``good`` to become bad.

    The general workflow steps are:

    - Choose a package

        - Do a bisect with just this package
        - save the result

    - Repeat with all packages

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

    def _choose_one(packages):
        return random.sample(packages, 1)[0]

    diff = _get_filtered_request_diff(good, bad)

    checked = set()
    bads = set()
    bad_packages = set()
    newer = diff.get(_NEWER)

    while True:
        candidates = set(newer.keys()) - checked - bads

        if not candidates:
            break

        chosen = _choose_one(candidates)
        chosen_diff = diff_mate.get_request_diff([chosen], diff)
        context = _get_approximate_bisect(has_issue, good, chosen_diff)

        if not has_issue(context):
            checked.add(chosen)

            continue

        bads.add(chosen)
        bad_packages.add(context.get_resolved_package(chosen))

    bad_package_map = {package.name: package for package in bad_packages}

    return diff_mate.filter_by_packages(bad_package_map, diff)


def bisect_2d(has_issue, good, bad):
    """Find the Rez package(s)/version(s) that cause ``good`` to become bad.

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
