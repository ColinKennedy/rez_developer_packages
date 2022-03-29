import os


def is_publishing_enabled():
    """bool: Check if the user's current environment is capable of publishing."""
    return os.getenv("REZ_EPH_REZ_SPHINX_FEATURE_DOCBOT_PLUGIN_REQUEST", "0").endswith(
        "1"
    )
