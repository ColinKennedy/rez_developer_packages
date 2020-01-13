- rename "verbose" to "details" and make "verbose" show logging statements
- change the clear option to allow you to clear just a single class, if needed

- Add a disable for context plugins
- Add a thing that checks what a checker requires
 - If the checker requires a context and it is disabled, disable the checker

- need a unittest to safely fallback loading a registered plugin fails, for any reason

TODO
  - C100 - author name is not a GitHub user or e-mail address

- Allow disables per-file
- CI
- Add unittests
 - make sure most of the tests (if not all) work with YAML files


# Checks

## Check Categories

- Convention - Basically like "warnings" but more situational
- Danger - These checks prevent issues within a package or for other packages
- Explain - Semantic errors. e.g. "Missing documentation". "No README". Things like that.


### Convention


Code|Description
semantic-versioning|Use versioning X.Y.Z (example: "1.0.0") for packaging


C100 - author name is not a GitHub user or e-mail address
C110 - not using semantic versioning


### Danger

|          Code           |                                      Description                                      |
|-------------------------|---------------------------------------------------------------------------------------|
| improper-requirements   | Adding Requirements to a Rez package that should be re-located                        |
| lower-bounds-missing    | Rez requirements should define lower bounds, to keep Rez resolves fast                |
| missing-requirements    | Auto-detected package requirements that aren't in the Rez package's ``requires`` list |
| no-rez-test             | Define tests for the Rez package. This goes without saying                            |
| not-python-definition   | Using anything other than a package.py to define a Rez package                        |
| requirements-not-sorted | Rez requirements need to be in alphabetical order                                     |
| too-many-dependencies   | When a Rez package has more dependencies that necessary                               |
| url-unreachable         | If Rez help refers to a missing website                                               |


#### requirements-not-sorted
When Rez package requirements aren't in alphabetical order, it causes
git merge conflicts whenever 2+ people edit requirements at the same
time. And it's an easily avoidable issue.


### Explain
E101 - requirements not explained
E110 - python package with no documentation
E120 - missing README
E121 - missing CHANGELOG

requirements-not-sorted : requirements not sorted
lower-bounds-missing : no lower bounds in requirements
