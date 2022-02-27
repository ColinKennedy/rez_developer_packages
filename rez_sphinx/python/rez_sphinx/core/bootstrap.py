"""Connect :ref:`Sphinx` to :ref:`rez_sphinx`."""


_REZ_SPHINX_BOOTSTRAP_LINES = (
    "from rez_sphinx import api",
    "locals().update(api.bootstrap(locals()))",
)


def _get_nearest_caller_package():
    raise NotImplementedError()


def append_bootstrap_lines(path):
    """Append :ref:`rez_sphinx` specific commands to a :ref:`Sphinx` conf.py file.

    Args:
        path (str):
            The absolute path to a conf.py which :ref:`Sphinx` uses to source
            and build the user's documentation.

    """
    with open(path, "a") as handler:
        handler.writelines(_REZ_SPHINX_BOOTSTRAP_LINES)


def bootstrap(data):
    package = _get_nearest_caller_package()

    data["name"] = package.name
    data["release"] = str(package.version)
    data["version"] = _get_major_minor(package.version)

    return data
