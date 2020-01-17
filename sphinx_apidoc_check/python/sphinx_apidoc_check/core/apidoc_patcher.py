#!/usr/bin/env python
# -*- coding: utf-8 -*-


_CREATION_TEXT = "Would create file "


def parse(text):
    to_add = set()

    for line in text.splitlines():
        if text.startswith(_CREATION_TEXT):
            to_add.add(line[len(_CREATION_TEXT) : -1])
        else:
            raise NotImplementedError(
                'Got line "{line}" but could not parse it.'.format(line=line)
            )

    return to_add
