#!/usr/bin/env python

import math
import subprocess

from rez import packages_
from rez import resolved_context
from rez.vendor.version import version as version_


_NEWER = "newer_packages"
_SUPPORTED_KEYS = frozenset((_NEWER, ))


def _get_full_context(context, diff):
    raise ValueError()


def _get_partial_context(context, diff, command):
    keys = set(diff.keys())
    unsupported = keys - _SUPPORTED_KEYS

    if unsupported:
        raise RuntimeError(
            'Unknown keys "{unsupported}" were found. Expected "{_SUPPORTED_KEYS}".'.format(
                unsupported=unsupported, _SUPPORTED_KEYS=_SUPPORTED_KEYS
            )
        )

    weight = 0.5
    newer = diff.get(_NEWER).values()
    previous = None

    while True:
        package_indices = dict()
        requests = []

        for packages in newer:
            index = math.floor(len(packages) * weight)
            package = packages[index]
            requests.append(package)
            package_indices[package.name] = index

        context = resolved_context.ResolvedContext(
            [
                "{package.name}=={package.version}".format(package=package)
                for package in requests
            ],
            package_paths=context.package_paths,
        )

        process = context.execute_command(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate()

        print('RET', process.returncode, weight)

        if process.returncode == 0:  # Success
            raise NotImplementedError(requests)
        else:
            weight /= 2

        if requests == previous:
            break
        else:
            previous = requests

    raise ValueError('Got this far')


def _group_by_family(diff):
    output = dict()

    for key, data in diff.items():
        output.setdefault(key, dict())

        for package in packages:
            output[key].setdefault(package.name, [])
            output[key][package.name].append(package)

        raise ValueError(output)


def run(bad, command, good=None):
    if not good:
        # TODO : Add test for this
        raise NotImplementedError("Need to write this")

    partial_context = _get_partial_context(good, good.get_resolve_diff(bad), command)
    # full_context = _get_full_context(partial_context, partial_context.get_resolve_diff(bad))

    # raise ValueError(full_context)
    # process = full_context.execute_shell(command)
