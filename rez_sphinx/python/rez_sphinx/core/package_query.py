def get_dependencies(package):
    variants = package.variants or []

    # TODO : Find the right variant to select, based on test requires
    if len(variants) != 1:
        # Ignore all variants if there's multiple. Let the
        # :ref:`build_documentation` rez-test handle which variant is selected.
        #
        variants = []
    else:
        variants = variants[0]

    return (package.requires or []) + variants
