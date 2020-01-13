#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Add a logging handler for this package."""

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
_LOGGER = logging.getLogger(__name__)
__HANDLER = logging.StreamHandler(stream=sys.stdout)
__FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
__HANDLER.setFormatter(__FORMATTER)
_LOGGER.addHandler(__HANDLER)
