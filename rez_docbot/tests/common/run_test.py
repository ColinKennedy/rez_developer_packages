"""All functions to make running unittest cases easier."""

import contextlib
import copy

from rez.config import config as config_


@contextlib.contextmanager
def keep_config():
    """Temporarily allow edits to `rez-config`_ for the scope of this function.

    Yields:
        module: The Rez temporary config object to modify.

    """
    if not hasattr(config_, "optionvars"):
        config_.optionvars = dict()

        yield config_

    optionvars = copy.deepcopy(config_.optionvars)

    try:
        yield config_
    finally:
        config_.optionvars = optionvars
