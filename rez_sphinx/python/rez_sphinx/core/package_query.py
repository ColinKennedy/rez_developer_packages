"""Find anything within Rez packages more easily."""


def get_dependencies(package):
    """Get the packages which ``package`` depends upon.

    This list doesn't return all dependencies. Just the ones that :ref:`rez_sphinx`
    requires in order to function.

    Args:
        package (rez.packages.Package): A Rez package to check.

    Returns:
        list[rez.packages.Package or rez.packages.Variant]:
            Each package or "variant of a package" which ``package`` needs
            during documentation-building.

    """
    base = (package.requires or [])
    variants = package.variants or []

    if not variants:
        return base

    if len(variants) != 1:
        # Ignore all variants if there's multiple. Let the
        # :ref:`_rez_sphinx.build_documentation_key` rez-test handle which
        # variant is selected.
        #
        variants = []
    else:
        variants = variants[0]

    return base + variants
