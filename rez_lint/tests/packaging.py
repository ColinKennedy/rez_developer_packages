#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import textwrap
import unittest

from python_compatibility.testing import common
from rez import packages_
from rez_utilities import creator, inspection


def _make_fake_source_package(name, text):
    directory = os.path.join(tempfile.mkdtemp("_some_rez_source_package"), name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(text)

    return directory


class BasePackaging(common.Common):
    def _make_installed_package(self, name, text):
        directory = _make_fake_source_package(
            name, text
        )

        package = packages_.get_developer_package(directory)
        new_package = creator.build(package, tempfile.mkdtemp())

        self.add_item(os.path.dirname(directory))
        self.add_item(inspection.get_packages_path_from_package(new_package))

        return new_package
