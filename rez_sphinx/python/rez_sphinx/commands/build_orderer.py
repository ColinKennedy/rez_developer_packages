def collect_packages(directories, searcher):
    packages = []
    found_names = set()
    found_uuids = dict()
    invalids = set()

    for directory in directories:
        for package in searcher(directory):
            if package.uuid:
                if package.uuid in found_uuids:
                    invalids.add(package)

                    continue

                found_uuids[package.uuid] = package.name

            if package.name in found_names:
                invalids.add(package)

                continue

            found_names.add(package.name)
            packages.append(package)

    return packages
