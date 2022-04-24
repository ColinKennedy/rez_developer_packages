"""Anything which could be used by multiple core modules."""

import collections

RepositoryDetails = collections.namedtuple(
    "RepositoryDetails", "group, repository, clone_url"
)
