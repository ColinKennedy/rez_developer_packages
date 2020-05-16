#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import atexit
import functools
import contextlib
import tempfile
import logging

from six.moves import StringIO
import rpm2cpio
from pyrpm import spec as spec_
import yumdownloader

_LOGGER = logging.getLogger(__name__)

@contextlib.contextmanager
def _keep_argv(value):
    existing = list(sys.argv)

    try:
        sys.argv[:] = value

        yield
    finally:
        sys.argv[:] = existing


def download_rpm_spec(name, directory):
    with _keep_argv(["yumdownloader", "--source", name, "--destdir", directory]):
        yumdownloader.YumDownloader()

    # This is the equivalent of
    # rpm2cpio ./xdotool-3.20150503.1-1.el7.src.rpm | cpio -civ '*spec'
    out_buffer = StringIO()

    rpm_path = next(os.path.join(directory, item) for item in os.listdir(directory) if item.endswith(".rpm"))
    _LOGGER.debug('Found RPM "%s".', rpm_path)

    with open(rpm_path, "r") as handler:
        rpm2cpio.rpm2cpio(stream_in=handler, stream_out=out_buffer)

    import cpiofile
    cpio = cpiofile.open(fileobj=out_buffer)
    print(cpio.extract("xdotools.spec"))
    # with open(tempfile.mktemp(prefix="rez_yum_installer_cpio_"), "wb") as handler:
    #     handler.write(out_buffer.getvalue())
    #
    # # We don't really need the cpio file (in fact it'd be great if we could just stream directly)
    # atexit.partial(functools.partial(os.remove, handler.name))


    # import sys
    # sys.path.append(os.path.join(os.path.expanduser('~'), 'env/config/rez_packages/utils/python'))
    # from inspection import dirgrep
    # dirgrep(out_buffer, '', sort=True)
    # print(out_buffer.getvalue())

    # spec_path = next(item for item in os.listdir(directory) if item.endswith(".spec"))
    #
    # return spec_.Spec.from_file(spec_path)
