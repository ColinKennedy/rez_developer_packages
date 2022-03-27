import collections

_Configuration = collections.namedtuple("_Configuration", "name, version")


def get_configuration(package):
    raise ValueError(package)


def get_repository(configuration):
    raise ValueError()


def create_repository(configuration):
    raise ValueError()
