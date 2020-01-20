#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that is concerned with parsing ``sphinx-apidoc``."""

_CREATION_TEXT = "Would create file "


def parse(text):
    r"""Find the files that a ``sphinx-apidoc`` command would need to create.

    Args:
        text (str):
            The raw stdout of a call to the ``sphinx-apidoc`` command
            (with --dry-run enabled). This text should always look
            something like "Would create file /foo/bar/thing.rst\nWould
            create file /foo/bar/another.rst".

    Raises:
        NotImplementedError:
            If a line is found in `text` that could be parsed. This
            should never happen but, if it does, it'd be a good
            indication that ``sphinx-apidoc`` changed their API.

    Returns:
        set[str]: The found files that ``sphinx-apidoc`` can see and discover.

    """
    to_add = set()

    for line in text.splitlines():
        if text.startswith(_CREATION_TEXT):
            to_add.add(line[len(_CREATION_TEXT) : -1])
        else:
            raise NotImplementedError(
                'Got line "{line}" but could not parse it.'.format(line=line)
            )

    return to_add
