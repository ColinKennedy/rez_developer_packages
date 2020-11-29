#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A basic module for determining whether the user wants symlinks or not while building."""

import sys


def must_symlink():
    """bool: Check if the user wants symlinks, not copy files."""
    return "--symlink" in sys.argv[1:]


def must_symlink_files():
    """bool: Check if the user wants symlinked files."""
    return "--symlink-files" in sys.argv[1:]


def must_symlink_folders():
    """bool: Check if the user wants symlinked folders."""
    return "--symlink-folders" in sys.argv[1:]
