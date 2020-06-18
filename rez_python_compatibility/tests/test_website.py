#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic unittests related to URLs and external websites."""

import unittest

from python_compatibility import website


class Urls(unittest.TestCase):
    """Make sure that URLs that should pass or fail do so at the correct times."""

    @unittest.skipIf(not website.is_internet_on(), "User has no interet conneciton.")
    def test_url_okay(self):
        """Check if Google is reachable (it always should be)."""
        self.assertTrue(website.is_url_reachable("https://www.google.com"))

    @unittest.skipIf(not website.is_internet_on(), "User has no interet conneciton.")
    def test_okay_002(self):
        """Check if Google's IP address is reachable (it always should be)."""
        self.assertTrue(website.is_url_reachable("http://216.58.192.142"))

    def test_url_missing(self):
        """A valid URL that points to a website that does not exist should fail."""
        self.assertFalse(
            website.is_url_reachable("https://www.a_website_that_does_not_exist.com")
        )

    def test_url_invalid(self):
        """A string that is not a valid URL should just return False."""
        self.assertFalse(
            website.is_url_reachable("asdflkasjdasflkjadsasdkljasfd:asdfalsdfkjasd")
        )
