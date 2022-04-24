"""All class interfaces needed by subclasses to work with :mod:`.publisher_`."""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Authenticator(object):
    """A base class to implement as subclasses."""

    def __init__(self, data):
        """Keep track of the validated ``data``. It will be queried / used later.

        Args:
            data (object):
                Any object needed for authentication purposes. Usually, this is
                a :class:`dict` but that isn't a requirement.

        """
        super(Authenticator, self).__init__()

        self._data = data

    @abc.abstractmethod
    def authenticate(self, uri):
        """Get a valid handle to the remote ``uri``.

        Args:
            uri (str):
                An addressable website. e.g. ``"https://www.github.com/Foo/bar"``
                or ``"git@github.com:Foo/bar"``

        Returns:
            Handler: The authenticated instance.

        """
        raise NotImplementedError("Implement this method in a subclass.")

    @classmethod
    @abc.abstractmethod
    def validate(cls, data, package):
        """Create an instance of this class, after checking ``data``.

        Args:
            data (object): Whatever input this class expects.

        Returns:
            Authenticator: The created instance.

        """
        raise NotImplementedError("Implement this method in a subclass.")


# TODO : Consider making this a function, instead of a class
@six.add_metaclass(abc.ABCMeta)  # pylint: disable=too-few-public-methods
class Handler(object):
    """An adapter class to make working with remote git services easier.

    This class helps initialize BaseRepository objects, which is where all of
    the "real" remote calls are going to be sent during publishing.

    """

    @abc.abstractmethod
    def get_repository(self, details, destination, auto_create=True):
        """Get or create a remote + cloned repository.

        Args:
            details (RepositoryDetails):
                A description of the repository full URL, the group it's nested
                under, and any other information that's important for cloning.
            destination (str):
                The absolute path to a directory on-disk to clone into. This
                path should be empty.
            auto_create (bool, optional):
                If the git repository doesn't already exist and ``auto_create``
                is True, make it and return the newly created repository.

        Returns:
            BaseRepository: The retrieved or created `GitHub`_ repository.

        """
        raise NotImplementedError("You must define this in a subclass.")


@six.add_metaclass(abc.ABCMeta)
class Publisher(object):
    """A base class for designing a documentation publisher.

    The main responsibilities of this class are

    - Cloning, copying, adding, pushing documentation
    - Authentication management (which may be delegated to other objects)

    """

    def __init__(self, data, package):
        """Store the information related to publishing.

        The ``data`` is assumed to be already validated. See
        :meth:`GenericPublisher.validate`.

        Args:
            data (dict[str, object]): Each git / remote data to save.
            package (rez.packages.Package): The object to publish.

        """
        super(Publisher, self).__init__()

        self._data = data
        self._package = package

    @classmethod
    @abc.abstractmethod
    def _get_schema(cls):
        """dict[object, object]: The required / optional structure for this instance."""
        raise NotImplementedError("Implement this in subclasses.")

    @abc.abstractmethod
    def is_required(self):
        """bool: Check if this publisher is expected to always have documentation."""
        return True

    @classmethod
    @abc.abstractmethod
    def get_name(cls):
        """str: The value used to refer to this class, as a :ref:`publisher type`."""
        return ""

    @abc.abstractmethod
    def get_resolved_repository_uri(self):
        """str: Get the URL / URI / etc to a remote git repository."""
        return ""

    @abc.abstractmethod
    def authenticate(self):
        """Connect this instance to the remote repository."""
        raise NotImplementedError("Implement this in subclasses.")

    @abc.abstractmethod
    def quick_publish(self, documentation):
        """Clone, copy, and push ``documentation`` as required.

        Args:
            documentation (str):
                The absolute directory to built documentation on-disk.

        """
        raise NotImplementedError("Implement this in subclasses.")

    @classmethod
    @abc.abstractmethod
    def validate(cls, data, package):
        """Store the information related to publishing.

        Args:
            data (dict[str, object]): Each git / remote data to save.
            package (rez.packages.Package): The object to publish.

        """
        return cls(data, package)
