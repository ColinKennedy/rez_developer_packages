``python_compatibility`` has 2 purposes

- Provide helper classes and functions to make working in Python easier
- Bridge the gap between Python 2 and 3

## About Dependencies

This package is not allowed to have any Rez package requirements except
for those related to Python 2 + 3 compatibility (such as six, backports,
futures, etc). These requirements will later be removed once Python 2
support is dropped.


## About Versioning

Every public function is considered part of this package's public "API".
So any breaking changes between versions requires a new major release.
