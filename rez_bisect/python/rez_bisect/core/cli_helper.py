import argparse
import os


class SplitPaths(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Strip each path, just in case there's unneeded whitespace
        setattr(namespace, self.dest, [value.strip() for value in values.split(os.pathsep)])
