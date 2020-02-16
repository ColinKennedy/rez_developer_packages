#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The entry point for the `move_break` CLI."""

import sys

from . import cli

cli.main(sys.argv[1:])
