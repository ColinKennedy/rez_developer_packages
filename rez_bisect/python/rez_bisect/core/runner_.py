#!/usr/bin/env python

import random
import math
import subprocess

from rez import packages_
from rez import resolved_context
from rez.vendor.version import version as version_


_NEWER = "newer_packages"
_SUPPORTED_KEYS = frozenset((_NEWER, ))


def _get_full_context(bad, diff, command):
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
        raise NotImplementedError('Need to make a while loop for this part.')

    raise ValueError('got this far')


def _get_partial_context(context, diff, command):
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
            package_paths=context.package_paths,
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
        package_paths=context.package_paths,
    )


def _check_command(context, command):
    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    process.communicate()

    return process.returncode == 0


def _to_request(request):
    return [
        "{package.name}=={package.version}".format(package=package)
        for package in request
    ]


def _validate_keys(diff):
    keys = set(diff.keys())
    unsupported = keys - _SUPPORTED_KEYS

    if unsupported:
        raise RuntimeError(
            'Unknown keys "{unsupported}" were found. Expected "{_SUPPORTED_KEYS}".'.format(
                unsupported=unsupported, _SUPPORTED_KEYS=_SUPPORTED_KEYS
            )
        )


def run(bad, command, good=None):
    if not good:
        # TODO : Add test for this
        raise NotImplementedError("Need to write this")

    partial_context = _get_partial_context(good, good.get_resolve_diff(bad), command)
    full_context = _get_full_context(partial_context, good.get_resolve_diff(partial_context), command)

    # raise ValueError(full_context)
    # process = full_context.execute_shell(command)
