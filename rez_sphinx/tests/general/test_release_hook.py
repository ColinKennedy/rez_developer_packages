import unittest


class PostRelease(unittest.TestCase):
    def test_invalid(self):
        raise ValueError()

    def test_normal(self):
        raise ValueError()
