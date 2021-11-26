from . import base


class Plugin(base.BuilderPlugin):
    # """A class that parses and builds documentation using Sphinx.
    #
    # See Also:
    #
    # """

    @staticmethod
    def get_name():
        """str: The name used to refer to this plug-in."""
        return "sphinx"

    def parse_arguments(text):
        parser = argparse.ArgumentParser(description="Tell Sphinx where the documentation lives and where to build it.")
        parser.add_argument("--source", help="The root folder containing your index.rst (or equivalent file).")
        parser.add_argument("--destination", help="The folder to build all documentation into.")

        return parser.parse_args(text)
