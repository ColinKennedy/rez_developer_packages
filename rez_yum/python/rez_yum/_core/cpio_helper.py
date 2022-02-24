import os

import libarchive


def _make_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def _make_entry_file(path, contents):
    directory = os.path.dirname(path)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    with open(path, "wb") as handler:
        handler.write(contents)


def extract(path, destination):
    with libarchive.Archive(path) as handler:
        for entry in handler:
            if entry.isdir():
                directory = os.path.join(destination, entry.pathname)

                _make_directory(directory)
            elif entry.isfile():
                contents = handler.read(entry.size)
                path = os.path.join(destination, entry.pathname)

                _make_entry_file(path, contents)
            # TODO : Re-add this later!!!
            # else:
            #     raise NotImplementedError(
            #         'Unsure how to process entry "{entry}".'.format(entry=entry)
            #     )
