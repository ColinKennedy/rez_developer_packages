#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import textwrap



def make_fake_source_package(name, text):
    directory = os.path.join(tempfile.mkdtemp("_some_rez_source_package"), name)
    os.makedirs(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(text)

    return directory
