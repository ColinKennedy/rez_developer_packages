#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import functools
import os
import shutil
import tempfile
import textwrap
import unittest


class Run(unittest.TestCase):
    def test_run(self):
        raise ValueError()


class Invalids(unittest.TestCase):
    def test_package_name(self):
        raise ValueError()

    def test_test_names(self):
        raise ValueError()


def _make_test_package():
    raise ValueError('Make nested, dependent Rez packages')

    directory = tempfile.mkdtemp(prefix="rez_test_env_package_")
    atexit.register(functools.partial(shutil.rmtree, directory))

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "foo_package_name"

                version = "1.0.0"

                tests = {
                    "name_A": {
                        "requires": ["python"]
                    }
                }
                """
            )
        )
