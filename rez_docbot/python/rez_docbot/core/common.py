"""Anything which could be used by multiple core modules.

Attributes:
    RepositoryDetails (collections.namedtuple):
        A description of the repository full URL, the group it's nested under,
        and any other information that's important for cloning.

"""

import collections

RepositoryDetails = collections.namedtuple(
    "RepositoryDetails", "group, repository, clone_url"
)
