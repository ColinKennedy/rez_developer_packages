#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The functions that ``rez_industry`` allows external packages to use."""

from .core.adapters.help_adapter import DEFAULT_HELP_LABEL
from .core.parser import add_to_attribute, remove_from_attribute

__all__ = ["DEFAULT_HELP_LABEL", "add_to_attribute", "remove_from_attribute"]
