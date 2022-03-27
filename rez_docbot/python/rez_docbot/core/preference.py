import schema

from rez.config import config

from . import adapter_registry, schema_type


_PUBLISHER = {
    "authentication": adapter_registry.validate,
    schema.Optional("inner_path"): schema_type.NON_EMPTY_STR,
    schema.Optional("latest_folder", default="latest"): schema_type.NON_EMPTY_STR,
    schema.Optional("publish_pattern", default=[schema_type.DEFAULT_PUBLISH_PATTERN]): schema_type.PUBLISH_PATTERNS,
    schema.Optional("required", default=True): bool,
    schema.Optional("version_folder", default="v"): str,  # TODO : Empty version_folder == no version folder
}

_MASTER_KEY = "rez_docbot"
_MASTER_SCHEMA = schema.Schema(
    {
        "publishers": [_PUBLISHER],
    }
)


def get_base_settings():
    rez_user_options = config.optionvars  # pylint: disable=no-member

    data = rez_user_options.get(_MASTER_KEY) or dict()

    return _MASTER_SCHEMA.validate(data)
