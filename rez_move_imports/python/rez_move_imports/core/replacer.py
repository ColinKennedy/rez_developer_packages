#!/usr/bin/env python
# -*- coding: utf-8 -*-


from move_break import cli
from python_compatibility import dependency_analyzer
from rez.vendor.version import requirement
from rez_industry import api


def _is_package_still_needed(package_namespaces, all_namespaces):
    for namespace in all_namespaces:
        if namespace.startswith(package_namespaces):
            return True

    return False


def _add_new_requirement_packages(paths, namespaces, deprecate):
    raise NotImplementedError('need to write this')


def _remove_deprecated_packages(paths, namespaces, deprecate):
    packages_to_remove = set()

    for package, package_namespaces in deprecate:
        if _is_package_still_needed(tuple(package_namespaces), namespaces):
            continue

        package = requirement.Requirement(package)
        packages_to_remove.add(package.name)

    code = ""
    api.remove_from_attribute("requires", list(packages_to_remove), code)
    raise NotImplementedError()


# TODO : Move this to a separate module
def replace(command, requirements, deprecate):
    overwritten_paths = cli.main(command) # Do the main replacement

    if not overwritten_paths:
        return

    paths = set()
    namespaces = dependency_analyzer.get_imported_namespaces(paths)

    _remove_deprecated_packages(paths, namespaces, deprecate)
    _add_new_requirement_packages(paths, namespaces, requirements)
