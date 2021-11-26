import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BuilderPlugin(object):
    @abc.abstractmethod
    def get_name():
        return ""
