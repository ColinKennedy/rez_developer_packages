import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Base(object):
    @classmethod
    @abc.abstractmethod
    def _get_schema(self):
        raise NotImplementedError("Implement this in subclasses.")

    @abc.abstractmethod
    def is_required(self, data):
        return True

    @classmethod
    @abc.abstractmethod
    def get_name(cls):
        return ""

    @abc.abstractmethod
    def get_resolved_repository_uri(self):
        return ""

    @abc.abstractmethod
    def authenticate(self):
        raise NotImplementedError("Implement this in subclasses.")

    @abc.abstractmethod
    def quick_publish(self, documentation):
        raise NotImplementedError("Implement this in subclasses.")

    @classmethod
    @abc.abstractmethod
    def validate(cls, data, package):
        raise NotImplementedError("Implement this in subclasses.")
