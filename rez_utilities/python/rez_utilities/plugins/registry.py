#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""An extend-able module for pipeline-specific Rez customizations."""

from . import url_manager

_URLS_LISTER_KEY = "search_urls_lister"
_PLUGINS = {_URLS_LISTER_KEY: url_manager.get_default_urls}


def get_help_url_templates():
    """list[str]: The (Python) documentation URL templates."""
    return _PLUGINS[_URLS_LISTER_KEY]()


def register_help_url_templates(caller):
    """Set the main function for finding Rez package URLs to the given `caller`.

    Args:
        caller (callable[:class:`rez.packages_.Package`] -> list[str]):
            The function that will be used to find URL templates.

    """
    _PLUGINS[_URLS_LISTER_KEY] = caller
