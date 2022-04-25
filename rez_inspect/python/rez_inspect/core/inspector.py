from __future__ import print_function


DEFAULT_STYLE = "pretty"
STYLES = {"python": repr, DEFAULT_STYLE: str}


def get_style(name):
    try:
        return STYLES[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" was invalid. Options were, "{options}".'.format(
                name=name, options=sorted(STYLES.keys())
            )
        )


def print_attributes(package, attributes, style=STYLES[DEFAULT_STYLE]):
    if len(attributes) == 1:
        value = style(getattr(package, attributes[0]))

        print(value)

        return

    for attribute in attributes:
        print("{attribute}:".format(attribute=attribute))
        value = style(getattr(package, attributes[0]))
        print("    {value}".format(value=value))
