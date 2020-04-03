#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run ``rez_symbl`` as a CLI, using the user's provided text."""

import sys

from . import cli

if __name__ == "__main__":
    cli.main(sys.argv[1:])
