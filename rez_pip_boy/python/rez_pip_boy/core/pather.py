import os


def normalize(path):
    return os.path.normcase(os.path.realpath(path))
