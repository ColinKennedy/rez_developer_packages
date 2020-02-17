#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import textwrap

from python_compatibility.testing import common


class Version(common.Common):
    def test_increment_minor(self):
        """Add a new value to a package's version without knowing what that version is."""
        directory = tempfile.mkdtemp(suffix="_test_increment_minor")
        self.delete_item_later(directory)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    """
                )
            )

    def test_decrement_minor(self):
        """Lower the value of a package's version without knowing what that version is."""
        directory = tempfile.mkdtemp(suffix="_test_decrement_minor")
        self.delete_item_later(directory)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    """
                )
            )

    def test_absolute_increment_minor(self):
        directory = tempfile.mkdtemp(suffix="_test_absolute_increment_minor")
        self.delete_item_later(directory)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    """
                )
            )

    def test_absolute_decrement_minor(self):
        directory = tempfile.mkdtemp(suffix="_test_absolute_decrement_minor")
        self.delete_item_later(directory)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    """
                )
            )

    def test_complex_details(self):
        """Write a really complex package.py file out, reliably, with a new version."""
        directory = tempfile.mkdtemp(suffix="_test_complex_details")
        self.delete_item_later(directory)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    """
                )
            )

    def test_format_yaml(self):
        directory = tempfile.mkdtemp(suffix="_test_format_yaml")
        self.delete_item_later(directory)

        with open(os.path.join(directory, "package.py"), "w") as handler:
            handler.write(
                textwrap.dedent(
                    """\
                    """
                )
            )

    def test_invalid_001(self):
        pass

    def test_invalid_002(self):
        pass
