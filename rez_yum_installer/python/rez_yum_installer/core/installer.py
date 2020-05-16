#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import logging
import os
import tempfile

import yum
import functools32
from six.moves import urllib
from rez import package_maker
from rez.config import config

from . import rpm_source_helper, textmate


_LOGGER = logging.getLogger(__name__)
_YUM_DATABASE = yum.YumBase()
_YUM_DATABASE.setCacheDir(force=True, tmpdir=tempfile.mkdtemp(prefix="rez_yum_installer_cache_dir_"), reuse=False)


def _download(name):
    directory = _get_rpm_temporary_directory()
    _get_built_rpm(name, directory)

    return rpm_source_helper.download_rpm_spec(name, directory)


def _get_built_rpm(name, directory):
    results = _YUM_DATABASE.pkgSack.returnNewestByNameArch(patterns=[name])

    if not results:
        # TODO : Replace with API exception
        raise RuntimeError('Name "{name}" could not be found in Yum.'.format(name=name))

    url = results[0].remote_url
    name = url.split("/")[-1]
    destination = os.path.join(directory, name)
    _LOGGER.info('Downloading "%s" to "%s" path.', url, destination)

    urllib.request.urlretrieve(results[0].remote_url, destination)


@functools32.lru_cache()
def _get_rpm_temporary_directory():
    return tempfile.mkdtemp(prefix="rez_yum_installer_rpm_install_directory_")


def _triage_requirements(requirements):
    paths = set()
    packages = set()

    for requirement in requirements:
        if os.path.isabs(requirement):
            paths.add(requirement)
        else:
            packages.add(requirement)

    return packages, paths


def install(name):
    spec = _download(name)

    build_requires = textmate.requirements_to_text(spec.build_requires)
    requires = textmate.requirements_to_text(spec.requires)

    build_requires, build_paths = _triage_requirements(build_requires)
    requires, paths = _triage_requirements(requires)

    invalids = set()

    for path in itertools.chain(build_paths, paths):
        if not os.path.exists(path):
            invalids.add(path)

    if invalids:
        raise RuntimeError('Required paths "{invalids}" do not exist.'.format(invalids=sorted(invalids)))

    with package_maker.make_package(textmate.convert_to_rez_package_name(spec.name), config.local_packages_path) as package:
        package.version = spec.version
        package.description = spec.summary

        if build_requires:
            package.build_requires = [textmate.convert_to_rez_package_name(requirement) for requirement in build_requires]

        if requires:
            package.requires = [textmate.convert_to_rez_package_name(requirement) for requirement in requires]

        package.help = [["Home Page", spec.url]]
