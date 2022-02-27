"""The module which managers user configuration settings.

Most of these functions are just thin wraps around :ref:`rez-config` calls.

"""

from rez.config import config


# TODO : Add caching here
def get_build_documentation_key():
    rez_sphinx_settings = _get_base_settings()

    return rez_sphinx_settings.get("build_documentation_key") or "build_documentation"


# TODO : Add caching here
def get_help_label():
    rez_sphinx_settings = _get_base_settings()

    return rez_sphinx_settings.get("help_label") or "rez_sphinx_objects_inv"


def _get_base_settings():
    return config.optionvars.get("rez_sphinx") or dict()


def _get_quick_start_overridable_options(overrides=tuple()):
    output = []

    if "--no-sep" not in overrides:
        output.append("--sep")  # if specified, separate source and build dirs

    if "--language" not in overrides and "-l" not in overrides:
        # Assume English, if no language could be found.
        output.extend(["--language", "en"])

    return output


def get_quick_start_options():
    # """list[str]: Any arguments to pass to sphinx-quickstart by default."""
    output = [  # These options are required to be part of the output
        "--author", "",
        "--ext-intersphinx",
        "--project", "",
        "--release", "",
        "-v", "",
    ]

    rez_sphinx_settings = _get_base_settings()
    settings = rez_sphinx_settings.get("sphinx-quickstart") or []

    if "--author" in settings or "-a" in settings:
        raise EnvironmentError('Do not provide any authors for rez-sphinx.')

    if "--project" in settings or "-p" in settings:
        raise EnvironmentError('Do not provide a project name for rez-sphinx.')

    if "--release" in settings or "-r" in settings:
        raise EnvironmentError('Do not provide a release version for rez-sphinx.')

    if "-v" in settings:
        raise EnvironmentError('Do not provide a project version for rez-sphinx.')

    if "--ext-intersphinx" in settings:
        settings.remove("--ext-intersphinx")

    output.extend(_get_quick_start_overridable_options(settings))

    return output
