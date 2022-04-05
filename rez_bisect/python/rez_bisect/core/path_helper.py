import os


def normalize(path, root):
    if os.path.isabs(path):
        return path

    return os.path.normcase(os.path.join(root, path))
