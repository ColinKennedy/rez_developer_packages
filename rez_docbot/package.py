name = "rez_docbot"

version = "1.0.0"

description = "Auto build, link, and publish documentation, via Rez"

authors = ["ColinKennedy"]


def commands():
    import os

    env.PYTHONPATH.append(os.path.join(root, "python"))
