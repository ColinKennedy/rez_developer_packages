from six.moves import mock

from rez_docbot.core import preference

from . import run_test


def get_quick_publisher(configuration, package=None):
    """Make a quick Publisher, based on ``configuration``.

    This function assumes that ``configuration`` only defines a single Publisher.

    Args:
        configuration (dict[str, object]):
            The :ref:`rez_docbot` preferences to use in order to create the Publisher.
        package (rez.packages.Package, optional):
            The Rez source package to query information from.

    Yields:
        :class:`rez_docbot.bases.base.Publisher`: The generated instance.

    """
    package = package or mock.MagicMock()

    try:
        del package.rez_docbot_configuration
    except AttributeError:
        pass

    with run_test.keep_config() as config:
        config.optionvars["rez_docbot"] = {"publishers": [configuration]}

        return preference.get_base_settings(package)["publishers"][0]
