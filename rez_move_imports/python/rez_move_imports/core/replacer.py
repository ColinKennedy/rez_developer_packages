#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main work-horse of ``rez_move_imports``. It actually does all the text replacement.

Both Python files and Rez package modules are manipulatable, using this module.

"""

from move_break import move_break_api
from python_compatibility import dependency_analyzer
from rez_bump import rez_bump_api
from rez_industry import api


def _is_package_needed(user_namespaces, all_namespaces):
    """Check if a Rez package's Python imports have anything in common with `all_namespaces`.

    Args:
        user_namespaces (tuple[str]):
            The user-provided namespaces that the user gave to
            the CLI. So for example if they add "--requirements
            some_package-1,thing,foo" then this list will end up being
            ["thing", "foo"].
        all_namespaces (iter[str]):
            The Python dot-separated namespaces that a Rez package uses.
            In short, these are all of the import statements that a
            Rez package has inside of it and can be thought of as its
            "dependencies". The function uses this list to figure out
            if `user_namespaces` is actually still being imported.

    Returns:
        bool:
            If all of the import namespaces in `user_namespaces` is
            still present in `all_namespaces`.

    """
    for namespace in all_namespaces:
        if is_matching_namespace(namespace, user_namespaces):
            return True

    return False


def _add_new_requirement_packages(package, namespaces, requirements):
    """Add new Rez package requirements to a Rez package, if needed.

    If no import statements were changed then this function does
    nothing. After all, if the imports of a package were changed then
    there's no way a Rez package's requirements should be any different.

    Args:
        package (:class:`rez.packges_.DeveloperPackage`):
            Some Rez package whose requirements may change as a result
            of this function getting ran.
        namespaces (iter[str]):
            The Python dot-separated namespaces that a Rez package uses.
            In short, these are all of the import statements that a
            Rez package has inside of it and can be thought of as its
            "dependencies". The function uses this list to figure out
            if `user_namespaces` is actually still being imported.
        requirements (iter[tuple[:class:`rez.vendor.version.requirement.Requirement`, tuple[str]]]):
            Each Rez package that might get added to `package` and a
            series of Python namespaces that the Rez package defines.
            If there's any overlap between the package's namespaces and
            the full `namespaces` then that means that `package` depends
            on the Rez package and so it is added as a dependency to
            `package`.

    """
    packages_to_add = set()

    for package_, package_namespaces in requirements:
        if not _is_package_needed(tuple(package_namespaces), namespaces):
            continue

        packages_to_add.add(str(package_))

    if not packages_to_add:
        # Nothing to do so exit early.
        return

    with open(package.filepath, "r") as handler:
        code = handler.read()

    new_code = api.add_to_attribute("requires", list(packages_to_add), code)

    with open(package.filepath, "w") as handler:
        handler.write(new_code)


def _remove_deprecated_packages(package, namespaces, deprecate):
    """Remove Rez package requirements from a Rez package, if needed.

    If the Python imports defined in `deprecate` are no longer present
    in `namespaces` then that means that `package` no longer depends
    on the stuff listed in `deprecate` and the requirement effectively
    doesn't matter anymore and can be removed.

    Args:
        package (:class:`rez.packges_.DeveloperPackage`):
            Some Rez package whose requirements may change as a result
            of this function getting ran.
        namespaces (iter[str]):
            The Python dot-separated namespaces that a Rez package uses.
            In short, these are all of the import statements that a
            Rez package has inside of it and can be thought of as its
            "dependencies". The function uses this list to figure out
            if `user_namespaces` is actually still being imported.
        deprecate (iter[tuple[:class:`rez.vendor.version.requirement.Requirement`, tuple[str]]]):
            Each Rez package that is (assumed to already be) a dependency of `package`
            and the Python import namespaces that the package takes up.

            If any namespace in `namespaces` is still around, then that
            means `package` actually still depends on the Rez package so
            we can't safely remove it (because it's still a dependency).
            But if it isn't there, remove it.

    """
    packages_to_remove = set()

    for package_, package_namespaces in deprecate:
        if _is_package_needed(package_namespaces, namespaces):
            continue

        packages_to_remove.add(package_.name)

    if not packages_to_remove:
        # Nothing to do so exit early.
        return

    with open(package.filepath, "r") as handler:
        code = handler.read()

    new_code = api.remove_from_attribute("requires", list(packages_to_remove), code)

    with open(package.filepath, "w") as handler:
        handler.write(new_code)


def is_matching_namespace(part, options):
    """Check if a Python namespace defines a parent namespace of `options`.

    Args:
        part (str):
            Some Python dot-separated namespace like "foo.bar".
        options (iter[str]):
            More Python dot-separated namespaces that may include `part`
            exactly like "foo.bar" or have a child namespace like
            "foo.bar.thing".

    Returns:
        bool:
            If `part` matches any namespace in `options` exactly or if
            any namespace in `options` starts with `part`.

    """
    for option in options:
        # Important, we add the trailing "." before running startswith
        # because we don't want similarly-named packages from returning
        # false-positives.
        #
        if part == option or part.startswith(option.rstrip(".") + "."):
            return True

    return False


def replace(package, configuration, deprecate, requirements, bump=True):
    """Replace as many Rez packages listed in `deprecate` with those listed in `requirements`.

    These packages get added / removed from `package` and written
    to-disk. This function isn't guaranteed to replace anything
    in `package`. It all depends on if, after changing the Python
    imports of the Python files in `configuration` if it looks like
    a dependency in `deprecate` isn't needed anymore, only then is
    it removed. Likewise, if the changed imports don't use anything
    in `requirements` then no new Rez packages will be added as
    dependencies to `package`, either.

    Args:
        package (:class:`rez.packges_.DeveloperPackage`):
            Some Rez package whose requirements may change as a result
            of this function getting ran. Requirements that originally
            existed may be removed. New requirements may be added.
        configuration (:attr:`move_break.cli.Configuration`):
            The user-provided options to the `move_break` package. It
            controls which Python modules will get their imports changed
            and how the imports will be changed.
        deprecate (iter[tuple[:class:`rez.vendor.version.requirement.Requirement`, tuple[str]]]):
            Each Rez package that is (assumed to already be) a
            dependency of `package` and the Python import namespaces
            that the package takes up.
        requirements (iter[tuple[:class:`rez.vendor.version.requirement.Requirement`, tuple[str]]]):
            Each Rez package that we'd like to add as dependencies to
            `package` followed by the Python dot-separated namespaces
            that each Rez package defines.
        bump (bool, optional):
            If True and `package` or its contents are modified,
            increment the minor version of `package` to reflect the new
            changes. If False, don't change the minor version of the Rez
            package even after new changes were made. Default is True.

    """
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

    namespaces = {
        module.get_namespace()
        for module in dependency_analyzer.get_imported_namespaces(configuration.paths)
    }
    _remove_deprecated_packages(package, namespaces, deprecate)
    _add_new_requirement_packages(package, namespaces, requirements)

    if bump and package.version:
        rez_bump_api.bump(package, minor=1, normalize=True)
