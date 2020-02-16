#!/usr/bin/env python
# -*- coding: utf-8 -*-


from move_break import move_break_api, cli
from python_compatibility import dependency_analyzer
from rez.vendor.version import requirement
from rez_industry import api


def _is_matching_namespace(part, options):
    for option in options:
        if part == option or part.startswith(option.rstrip(".") + "."):
            return True

    return False


def _is_new_requirement_needed():
    for namespace in all_namespaces:
        if namespace.startswith(package_namespaces):
            return True

    return False


def _is_package_still_needed(package_namespaces, all_namespaces):
    for namespace in all_namespaces:
        if _is_matching_namespace(namespace, package_namespaces):
            return True

    return False


def _add_new_requirement_packages(package, namespaces, deprecate):
    packages_to_add = set()

    for package_, package_namespaces in deprecate:
        if not _is_package_still_needed(tuple(package_namespaces), namespaces):
            continue

        package_ = requirement.Requirement(package_)
        packages_to_add.add(str(package_))

    with open(package.filepath, "r") as handler:
        code = handler.read()

    new_code = api.add_to_attribute("requires", list(packages_to_add), code)

    with open(package.filepath, "w") as handler:
        handler.write(new_code)


def _remove_deprecated_packages(package, namespaces, deprecate):
    packages_to_remove = set()

    for package_, package_namespaces in deprecate:
        if _is_package_still_needed(tuple(package_namespaces), namespaces):
            continue

        package_ = requirement.Requirement(package_)
        packages_to_remove.add(package_.name)

    with open(package.filepath, "r") as handler:
        code = handler.read()

    new_code = api.remove_from_attribute("requires", list(packages_to_remove), code)

    with open(package.filepath, "w") as handler:
        handler.write(new_code)


# TODO : Move this to a separate module
def replace(package, configuration, requirements, deprecate):
    # Replace Python imports in all of the paths in `configuration`
    overwritten_paths = move_break_api.move_imports(
        configuration.paths,
        configuration.namespaces,
        partial=configuration.partial_matches,
        import_types=configuration.types,
        aliases=configuration.aliases,
    )

    if not overwritten_paths:
        return

    namespaces = {module.get_namespace() for module in dependency_analyzer.get_imported_namespaces(configuration.paths)}
    _remove_deprecated_packages(package, namespaces, deprecate)
    _add_new_requirement_packages(package, namespaces, requirements)
