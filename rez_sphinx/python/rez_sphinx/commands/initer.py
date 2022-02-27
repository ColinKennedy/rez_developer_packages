"""The module which handles the :ref:`rez_sphinx init` command."""

import logging
import os

from sphinx.cmd import quickstart

from ..core import bootstrap, package_change, preference, sphinx_helper

_LOGGER = logging.getLogger(__name__)


def _run_sphinx_quickstart(directory, options=tuple()):
    options = options or []
    arguments = [directory] + options

    _LOGGER.debug('Got sphinx-quickstart arguments "%s".', arguments)
    _LOGGER.info('Now running sphinx-quickstart in "%s" folder.', directory)

    quickstart.main(arguments)

    path = sphinx_helper.find_configuration_path(directory)

    if not os.path.isfile(path):
        raise RuntimeError('Something went wrong, "{path}" was not defined.'.format(path=path))

    return path


def init(package, directory, quick_start_options=tuple()):
    # """Connect the Rez package at ``directory`` to :ref:`rez_sphinx`.
    #
    # Warning:
    #     This function generates many files directly underneath ``directory``.
    #     Save your work first before running this function!
    #
    #
    # """
    options = quick_start_options or preference.get_quick_start_options()
    configuration_path = _run_sphinx_quickstart(directory, options=options)
    bootstrap.append_bootstrap_lines(configuration_path)

    package_change.initialize_rez_package(package)
