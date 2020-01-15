rez_lint is a "pylint-inspired" tool that checks Rez packages for issues.

Now, Rez does a great job catching problems with packages. This list
catches the issues that Rez doesn't already. The kinds of checks that
you didn't know you needed.


# Checks

## All Categories

- Danger - These checks prevent issues within a package or for other packages.
- Explain - Similar to danger. These issues mark documentation-related problems.
- Convention - Basically like "warnings" but more situational.


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


### Explain

|       Code       |                             Description                             |
|------------------|---------------------------------------------------------------------|
| no-change-log    | Need a CHANGELOG.md / CHANGELOG.rst / etc for the package           |
| no-documentation | Missing documentation in a Python package                           |
| no-read-me       | Package has no summary information. What does it do, its rules, etc |
| needs-comment    | A package requirement needs an explanation                          |


### Convention

|        Code         |                                     Description                                      |
|---------------------|--------------------------------------------------------------------------------------|
| semantic-versioning | Use versioning X.Y.Z (example: "1.0.0") for packaging                                |
| bad-author          | Author names should either be a valid GitHub user name, full name, or e-mail address |


# Check Details

Now that every issue check is listed, here's some quick information
about **why** these checks need to exist (listed in alphabetical order).


## bad-author

In a Rez package, use your full name (the full name that's listed on
GitHub), your GitHub user name, or e-mail address. You can also use any
combination of these, if you want.

```python
authors = [
	"Colin Kennedy (my@mail.com)",
]
```

## improper-requirements

If a dependency package requires "mock-1" and another package has a
package.py that looks like this:

```python
requires = [
	"dependency-1",  # This uses mock-1
]

tests = {
	"unittest": {
		"requires": [
			"mock-2+",
		],
	}
}
```

The Rez resolve will fail because dependency's requirement on mock conflicts
with the current package.

Same goes with build dependencies. They should not be in any ``requires``.
It should be in either build_requires or private_build_requires.

That way, you never end up in a situation like this

```python
private_build_requires = [
	"cmake-3",
]

requires = [
	"dependency-1",  # This uses cmake-2.8
]
```

If "dependency" also uses ``private_build_requires``, there'd be no problems.


## lower-bounds-missing

In short, always specify a minimum version, even if that version is the
1.0.0 release of a package.

```python
requires = [
	"dependency-2",  # Do this
	"another_dependency",  # Do not do this
]
```

Rez has to take into account every version range in a every package
request for a resolve. So the tighter the requirements, the faster Rez
can resolve.


## needs-comment

Ever see a list of 20 requirements in a Rez package and you have no idea
if any of them are needed? Hopefully you'll never be in this situation
where you must refactor one of these packages. But if you are, you'll be
grateful for comments.

This checker is simple. If the Rez package defines at least one Python package,
``rez_lint`` ...

- finds every Rez package dependency based on the imported Python modules across all files
- gets a list of the "actually used" Rez packages from those imports
- checks this found list against the package's actual ``requires``

Anything in the ``requires`` that wasn't from imports needs a comment
explaining why that dependency is there.


## no-change-log

The Rez package should have a CHANGELOG file at its root to explain what
was changed. It can be any file format, CHANGELOG.rst, CHANGELOG.md,
CHANGELOG.txt, anything. If writing a Python package, it's recommended
to use CHANGELOG.rst though because it can then be added to Sphinx
documentation automatically.

Here's an example of the "Sphinx automatic import" feature.

A CHANGELOG written as .rst at a Rez package root
- https://github.com/ColinKennedy/sphinx-code-include/blob/master/CHANGELOG.rst

can then be included in Sphinx documentation, like this
- https://github.com/ColinKennedy/sphinx-code-include/blob/master/docs/changelog.rst

And here's a link to what the final result looks like
- https://sphinx-code-include.readthedocs.io/en/latest/changelog.html

Basically, you only need to maintain one file if you use the .rst extension.


## no-documentation

If the Rez package defines a Python package, that package is expected to
have Sphinx documentation. The documentation format that it checks for is
[in this Python code](https://github.com/ColinKennedy/rez_developer_packages/blob/07d92ddd15b3650f39c76387eb598ada64edd202/python_compatibility/python/python_compatibility/sphinx/conf_manager.py#L93-L130)


## no-read-me

This one is simple. Every Rez package should have a README.md, README.rst, or README.txt
to explain what the package is for.

Really take the extra effort to flesh out details about the package.

- describe what the package does
- package requirements
- feature road map
- style guide information
- contributor guidelines

Things like that help a lot for new starters or people who stumble on the code.


## no-rez-test

Unless the Rez package is meant for configuration, chances are
the package implements some code. Your code should be tested,
always, when users are involved. Define tests using the package's
[test](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#te
sts) attribute.


## not-python-definition

Rez definition files should be package.py. Though other standards
exist, do not use them. For example, you could define a package using
package.yaml. If you're dealing with a code-base that uses package.yaml,
run ``rez-yaml2py`` and Rez will handle the conversion for you.


## requirements-not-sorted

We've reached the "nitpick" portion of ``rez_lint``. But it's a valid nitpick.

Imagine a Rez package.py that has these requirements

```python
requires = [
    "my_package-1",
    "another_package-5",
]
```

If requirements are not sorted, they have a higher likelihood of
creating git merge conflicts when developers modify a package definition
file at the same time. Instead of losing time to merge conflicts, run a
quick alphabetical sort:

```python
requires = [
    "another_package-5",
    "my_package-1",
]
```

and you don't have to worry about that anymore.


## semantic-versioning

The Rez documentation recommends [semantic versioning](https://github.com/nerdvegas/rez/wiki/Basic-Concepts#versions).
So ``rez_lint`` also recommend it.


## too-many-dependencies

Having many dependencies in a Rez package is a strong indication that
the code can be restructured. It also limits the package's portability
and usefulness to others because anyone that uses a 10+ dependency
package is now, by extension, concerned with those dependencies.

If you are writing a package uses many dependencies, consider using
[Dependency Inversion](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
or [Dependency injection](https://en.wikipedia.org/wiki/Dependency_injection)
so that you can simply supply packages in the user's ``rez-env`` request
instead of adding it directly into the Package.


## url-unreachable

The rez-help command is determined by written [help
attribute](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guid
e#help) in the Rez package.py

This check simply makes sure that the URL is still good. Also, if the
Internet is down, the check will simply return "all good" to prevent CI
checks to prevent developers from releasing code.


# TODO

- TODO finish bad-author
- Add unittests


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


