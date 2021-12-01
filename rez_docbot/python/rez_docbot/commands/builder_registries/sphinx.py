"""A class that parses and builds documentation using Sphinx."""

import argparse

from . import base


class Plugin(base.BuilderPlugin):
    """A class that parses and builds documentation using Sphinx.

    See Also:
        https://www.sphinx-doc.org/en/master/index.html

    """

    @staticmethod
    def get_name():
        """str: The name used to refer to this plug-in."""
        return "sphinx"

    @staticmethod
    def build(namespace):
        raise NotImplementedError('Need to write this')

    @staticmethod
    def parse_arguments(text):
        """Get the source folder to find documentation and a build folder to send it to.

        Args:
            text (list[str]): The raw user-provided input to parse. e.g.
                ["build", "sphinx", "--", "--source", "documentation/source",
                "--destination", "documentation/build"].

        Returns:
            :class:`argparse.ArgumentParser`:
                The parsed, required and optional arguments needed to build the
                Sphinx documentation.

        """
        parser = argparse.ArgumentParser(
            description="Tell Sphinx where the documentation lives and where to build it."
        )
        # TODO : Needs required=True
        parser.add_argument(
            "--source",
            required=True,
            help="The root folder containing your index.rst (or equivalent file).",
        )
        parser.add_argument(
            "--destination", help="The folder to build all documentation into."
        )

        return parser.parse_args(text)
