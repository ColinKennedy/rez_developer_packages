import logging
import sys

_LOGGER = logging.getLogger(__name__)
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.INFO)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)
