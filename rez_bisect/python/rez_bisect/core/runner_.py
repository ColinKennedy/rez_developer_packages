#!/usr/bin/env python

"""The module which bisects Rez contexts to determine where an issue was introduced."""

import math
import random
import subprocess

from rez import resolved_context

_NEWER = "newer_packages"
_SUPPORTED_KEYS = frozenset((_NEWER,))


def _get_full_context(bad, diff, command):
    """Check groups of Rez packages to find the best resolve which starts to fail `command`.

    Unlike :func:`_get_partial_context`, which is only meant to get a
    context which is near the root of the problem, this function should
    always return a context which is very close (if not exactly on)
    where `command` begins to fail.

    Args:
        bad (:class:`rez.resolved_context.ResolvedContext`):
            The context which fails to run `command`.
        diff (dict[str, list[:class:`rez.utils.formatting.PackageRequest`]]):
            Each type of Rez package (added, newer, older, removed, etc)
            and each version found between `bad` and a working resolve.
        command (str):
            The path to a shell script which, when run, will pass or succeed.

    Raises:
        NotImplementedError: This function is still WIP.

    Returns:
        :class:`rez.resolved_context.ResolvedContext`:
            The context which determines the exact context where
            `command` starts failing.

    """
    _validate_keys(diff)

    newer_packages = diff.get(_NEWER)
    keys = set(newer_packages.keys())
    package_selection = random.sample(keys, (len(newer_packages) // 2) + 1)
    bad_packages = {variant.name: variant for variant in bad.resolved_packages}

    for name in package_selection:
        working_package = newer_packages[name][0]
        bad_packages[name] = working_package

    context = resolved_context.ResolvedContext(
        _to_request(bad_packages.values()),
        package_paths=bad.package_paths,
    )

    if not _check_command(context, command):
        # TODO : Add support for this later
        raise NotImplementedError("Need to make a while loop for this part.")

    raise ValueError("got this far")


# TODO : Simplify these parameters, if possible
def _get_partial_context(good, diff, command):
    """Check all Rez package at once to find a close-ish match that fails `command`.

    The objective of this is not to get a perfect context which shows
    exactly when `command` begins to fail. The objective is to get close
    enough so other functions can begin finessing to find the best
    context.

    For a more exact match, see :func:`_get_full_context`.

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
    _validate_keys(diff)

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

        if not _check_command(checker_context, command):
            weight /= 2

            continue

        if request == previous:
            break
        else:
            weight *= 1.5
            previous = request

    closest_newer = {key: value + 1 for key, value in newer_indices.items()}
    request = [newer_packages[key][index] for key, index in closest_newer.items()]

    return resolved_context.ResolvedContext(
        _to_request(request),
        package_paths=good.package_paths,
    )


def _check_command(context, command):
    """Check if `context` can run `command` without failing.

    Args:
        context (:class:`rez.resolved_context.ResolvedContext`):
            A Rez resolve which might fail if it runs `command`.
        command (str):
            The path to a shell script which, when run, will pass or succeed.

    Returns:
        bool: If the `command` succeeded.

    """
    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    process.communicate()

    return process.returncode == 0


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
    partial_context = _get_partial_context(good, good.get_resolve_diff(bad), command)
    full_context = _get_full_context(
        partial_context, good.get_resolve_diff(partial_context), command
    )

    raise ValueError(full_context)
    # process = full_context.execute_shell(command)
