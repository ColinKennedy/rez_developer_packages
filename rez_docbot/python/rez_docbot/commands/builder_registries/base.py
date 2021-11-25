import abc

import six

@six.add_metaclass(abc.ABCMeta)
class Plugin(object):
    @abc.abstractmethod
    def get_name():
        return ""
