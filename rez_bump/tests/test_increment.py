#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import textwrap

from python_compatibility.testing import common
from rez_utilities import increment, inspection


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
                    name = "my_complex_rez_package"

                    description     = (
                        "Abominable whitespace "
                        "because we can."
                    )

                    authors = [
                        "Some first / last name",
                            "John Doe",
                    ]

                    version    = \
                        "1.0.0"

                    # I am commented information
                    help = [
                        ["README", "README.md"],
                        ["Home Page", "http://google.com"],
                    ]

                    @late()
                    def requires():
                        if in_context():
                            return ["foo"]

                        return ["bar"]



                    variants = [
                        ["python-2.7", "more_packages", "here"],
                        ["python-3"],
                    ]


                    def commands():
                        import os

                        env.THING.set("something_here")
                        env.PYTHONPATH.append(os.path.join("{root}", "python"))
                    """
                )
            )

        package = inspection.get_nearest_rez_package(directory)
        package = increment.bump(package, minor=3)

        with open(package.filepath, "r") as handler:
            code = handler.read()

        expected = textwrap.dedent(
            """\
            name = "my_complex_rez_package"

            description     = (
                "Abominable whitespace "
                "because we can."
            )

            authors = [
                "Some first / last name",
                    "John Doe",
            ]

            version    = \
                "1.3.0"

            help = [
                ["README", "README.md"],
                ["Home Page", "http://google.com"],
            ]

            @late()
            def requires():
                if in_context():
                    return ["foo"]

                return ["bar"]



            variants = [
                ["python-2.7", "more_packages", "here"],
                ["python-3"],
            ]


            def commands():
                import os

                env.THING.set("something_here")
                env.PYTHONPATH.append(os.path.join("{root}", "python"))
            """
        )

        self.assertEquals(expected, code)

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
