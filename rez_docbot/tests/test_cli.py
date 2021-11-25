import unittest


class DelimiterCases(unittest.TestCase):
    def test_help_with_no_delimiter(self):
        """Show the general help."""
        raise ValueError()

    def test_incomplete_left_arguments(self):
        raise ValueError()

    def test_incomplete_right_arguments(self):
        raise ValueError()

    def test_help_is_left_of_delimiter(self):
        """Show the general help."""
        raise ValueError()

    def test_help_is_right_of_delimiter(self):
        """Show the plug-in help."""
        raise ValueError()

    def test_provided(self):
        """Pass execution."""
        raise ValueError()


class BuilderRegistry(unittest.TestCase):
    def test_not_found(self):
        """Error if the provided plug-in name does not exist."""
        raise ValueError()

    def test_found_known(self):
        """Find a provided plug-in."""
        raise ValueError()

    def test_found_user(self):
        """Find a user-provided plug-in."""
        raise ValueError()
