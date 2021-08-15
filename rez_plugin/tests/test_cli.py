"""Make sure the command-line works as expected."""

import unittest


class Cli(unittest.TestCase):
    """Make sure the basics of the command-line works as expected."""

    def test_command(self):
        """Register a command and call it, via the plug-in manager."""
        raise ValueError()

    def test_null_001(self):
        """Call the plug-in manager with no registered plugins."""
        raise ValueError()

    def test_null_002(self):
        """Call the plug-in manager with a registered, empty plugin."""
        raise ValueError()


class Invalid(unittest.TestCase):
    """All invalid inputs into rez-plugin."""

    def test_unknown_plugin(self):
        """Fail to call a plug-in that does not exist."""
        raise ValueError()
