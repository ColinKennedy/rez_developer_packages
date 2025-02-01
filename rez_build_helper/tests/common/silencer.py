"""Control and quiet as much stdout / stderr prints as possible."""

import contextlib
import typing


def _can_use_wurlizer() -> bool:
    try:
        import wurlitzer as _  # pylint: disable=import-outside-toplevel
    except ImportError:
        return False

    return True


if _can_use_wurlizer():
    # This branch is basically for Linux, which can use wurlitzer

    @contextlib.contextmanager
    def get_context() -> typing.Generator[typing.Tuple[str, str], None, None]:
        """:class:`contextlib.GeneratorContextManager`: Silence all C-level stdout messages."""
        import wurlitzer  # pylint: disable=import-outside-toplevel,import-error

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
    # This branch is basically for Windows, which cannot use wurlitzer
    import ctypes
    import io
    import os
    import sys
    import tempfile

    # References:
    #
    #     - https://gist.github.com/natedileas/8eb31dc03b76183c0211cdde57791005
    #     - https://github.com/minrk/wurlitzer/issues/12
    #
    if sys.version_info < (3, 5):
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
    else:
        if hasattr(sys, "gettotalrefcount"):  # debug build
            libc = ctypes.CDLL("ucrtbased")
        else:
            libc = ctypes.CDLL("api-ms-win-crt-stdio-l1-1-0")

    # c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
    kernel32 = ctypes.WinDLL("kernel32")  # type: ignore
    STD_OUTPUT_HANDLE = -11
    c_stdout = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    ##############################################################

    @contextlib.contextmanager
    def get_context() -> typing.Generator[typing.Tuple[str, str], None, None]:
        """Silence all writes to stdout."""
        stream = io.BytesIO()
        # The original fd stdout points to. Usually 1 on POSIX systems.
        original_stdout_fd = sys.stdout.fileno()

        def _redirect_stdout(to_fd: int) -> None:
            """Redirect stdout to the given file descriptor."""
            # Flush the C-level buffer stdout
            libc.fflush(None)  #### CHANGED THIS ARG TO NONE #############
            # Flush and close sys.stdout - also closes the file descriptor (fd)
            sys.stdout.close()
            # Make original_stdout_fd point to the same file as to_fd
            os.dup2(to_fd, original_stdout_fd)
            # Create a new sys.stdout that points to the redirected fd
            sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, "wb"))

        # Save a copy of the original stdout fd in saved_stdout_fd
        saved_stdout_fd = os.dup(original_stdout_fd)

        try:
            # Create a temporary file and redirect stdout to it
            tfile = tempfile.TemporaryFile(mode="w+b")
            _redirect_stdout(tfile.fileno())
            # Yield to caller, then redirect stdout back to the saved fd
            yield ("", "")
            _redirect_stdout(saved_stdout_fd)
            # Copy contents of temporary file to the given stream
            tfile.flush()
            tfile.seek(0, io.SEEK_SET)
            stream.write(tfile.read())
        finally:
            tfile.close()
            os.close(saved_stdout_fd)
