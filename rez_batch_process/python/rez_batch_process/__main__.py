#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that controls the command-line's interface."""

from __future__ import print_function

import logging
import sys

from . import cli


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    cli.main(sys.argv[1:])
