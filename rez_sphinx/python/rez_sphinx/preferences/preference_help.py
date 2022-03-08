import schema

from . import preference_help_


DEFAULT = schema.Use(preference_help_.alphabetical)
OPTIONS = {
    "alphabetical": preference_help_.alphabetical,
    "prefer_generated": preference_help_.prefer_generated,
    "prefer_original": preference_help_.prefer_original,
    "preserve_order": preference_help_.preserve_order,
}


def validate_order(item):
    try:
        return OPTIONS[item]
    except KeyError:
        raise ValueError(
            'Item "{item}" is invalid. Options were. "{options}".'.format(
                item=item, options=sorted(OPTIONS.keys())
            )
        )

