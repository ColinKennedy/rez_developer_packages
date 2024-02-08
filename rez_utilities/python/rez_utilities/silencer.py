"""Control and quiet as much stdout / stderr prints as possible."""

import contextlib


def _can_use_wurlizer():
    try:
        import wurlitzer as _  # pylint: disable=import-outside-toplevel
    except ImportError:
        return False

    return True


if _can_use_wurlizer():
    # This branch is basically for Linux, which can use wurlitzer

    @contextlib.contextmanager
    def get_context():
        """:class:`contextlib.GeneratorContextManager`: Silence all C-level stdout messages."""
        import wurlitzer  # pylint: disable=import-outside-toplevel

        with wurlitzer.pipes() as (stdout, stderr):
            yield (stdout, stderr)

        # We need to close the pipes or we get warnings in Python 3+ unittests
        #
        # Warnings like this:
        #
        # /usr/lib64/python3.6/contextlib.py:88:
        # ResourceWarning: unclosed file <_io.TextIOWrapper ...>
        #
        stdout.close()
        stderr.close()

else:

    @contextlib.contextmanager
    def get_context():
        """Don't silence anything."""
        yield
