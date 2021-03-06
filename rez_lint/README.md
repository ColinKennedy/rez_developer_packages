``rez_lint`` is a "pylint-inspired" tool that checks Rez packages for issues.

Rez does a great job catching problems with packages, already.
``rez_lint`` extends these checks to make Rez packages even more stable
and problem-free.


# How To Run
## From Shell

cd into your Rez package and run ``rez_lint``

```sh
rez-env rez_lint -- rez_lint
```

The tool will check the package for issues and report them

## From rez-test

Simply add this to your Rez package definition

```python
tests = {
	"rez_lint": {
		"command": "rez_lint",
		"requires": ["rez_lint"],
	},
}
```


# Features

Run recursively (checking every found Rez package under a folder)

```sh
rez_lint --recursive
```

Output the issues a vimgrep-style location list

```sh
rez_lint --vimgrep
package.py:6:0:version = "1.0" (semantic-versioning)
package.py:12:0:requires = [ (lower-bounds-missing)
```

Disable 1-or-more checks

```sh
rez_lint --disable=no-change-log,lower-bounds-missing
```


# Checks
## All Categories

- Danger - These checks prevent issues within a package or for other packages.
- Explain - Similar to danger. These issues mark documentation-related problems.
- Convention - Basically like "warnings" but more situational.


### Danger

|               Code               |                                            Description                                            |
|----------------------------------|---------------------------------------------------------------------------------------------------|
| duplicate-build-requires         | The ``build_requires`` attribute cannot list the same Rez package family more than once.          |
| duplicate-private-build-requires | The ``private_build_requires`` attribute cannot list othe same Rez package family more than once. |
| duplicate-requires               | The ``requires`` attribute cannot list othe same Rez package family more than once.               |
| improper-requirements            | Adding Requirements to a Rez package that should be re-located                                    |
| invalid-schema                   | Your package definition isn't a valid Rez package                                                 |
| lower-bounds-missing             | Rez requirements should define lower bounds, to keep Rez resolves fast                            |
| missing-requirements             | Auto-detected package requirements that aren't in the Rez package's ``requires`` list             |
| no-rez-test                      | Define tests for the Rez package. This goes without saying                                        |
| no-uuid                          | The package must define a ``uuid`` so that it doesn't overwrite another package by accident.      |
| not-python-definition            | Using anything other than a package.py to define a Rez package                                    |
| requirements-not-sorted          | Rez requirements need to be in alphabetical order                                                 |
| too-many-dependencies            | When a Rez package has more dependencies that necessary                                           |
| url-unreachable                  | If Rez help refers to a missing website                                                           |


### Explain

|       Code       |                             Description                             |
|------------------|---------------------------------------------------------------------|
| needs-comment    | A package requirement needs an explanation                          |
| no-change-log    | Need a CHANGELOG.md / CHANGELOG.rst / etc for the package           |
| no-documentation | Missing documentation in a Python package                           |
| no-help          | Need to define the ``help`` attribute in your Rez definition file   |
| no-read-me       | Package has no summary information. What does it do, its rules, etc |


### Convention

|        Code         |                                     Description                                      |
|---------------------|--------------------------------------------------------------------------------------|
| semantic-versioning | Use versioning X.Y.Z (example: "1.0.0") for packaging                                |


# Check Details

Now that every issue check is listed, here's some quick information
about **why** these checks need to exist (listed in alphabetical order).


## duplicate-build-requires / dupicate-requires / dupicate-build-requires

The next 3 checks have the same logic and meaning, so they've been
grouped into a single section. In short, these checkers cover 3
attributes that Rez uses to define package dependencies.

- [build_requires](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_requires)
- [private_build_requires](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#private_build_requires)
- [requires](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#requires)

Each attribute expects a list and looks like this:

```python
requires = [
	"python-2",
	"rez-2",
	"some_dependency-1+",
]
```

But sometimes, people sometimes make the mistake of listing the same
Rez package more than once.

```python
requires = [
	"python-2",
	"some_dependency-1+"  # Duplicate "some_dependency"
	"rez-2",
	"some_dependency-2+<3",  # Duplicate "some_dependency"
]
```

These checkers make sure that the ``requires``, ``build_requires``, and
``private_build_requires`` attributes don't accidentally have duplicates.


## improper-requirements

Some Rez packages should not be direct requirements of other packages.
For example, you shouldn't add "mock" or "cmake" or "pytest" as
dependencies of your package.

Unittest / integration test packages should go in your [tests](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests)
attribute. Build packages such as "cmake" should go either in the Rez package's [private_build_requires](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#private_build_requires)
or [build_requires](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#build_requires).

In summary, that's basically all you need to know. Feel free to skip
to the next section. But if you want to know more **why** this is
recommended, please keep reading.

Imagine you have a package like this

```python
requires = [
    "dependency-1",  # This package's `requires` includes mock-1
]

tests = {
    "unittest": {
        "requires": [
            "mock-2+",
        ],
    }
}
```

The Rez resolve will fail because dependency's requirement on mock
conflicts with the current package. But if "dependency-1" added "mock-1"
in its ``tests``, there would have been no issues at all.

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

If "dependency-1" also uses ``private_build_requires``, there'd be no problems.


## invalid-schema

If your package has an issue which would prevent Rez from reading it,
that error is pointed out by rez-lint. The error isn't one specific
issue, it could be anything.


## lower-bounds-missing

In short, always specify a minimum version, even if that version is the
1.0.0 release of a package.

```python
requires = [
    "dependency-2",  # Do this
    "dependency",  # Do not do this
]
```

Rez has to take into account every version range in a every package
request for a resolve. So the tighter the requirements, the faster Rez
can resolve. Code-bases that don't use minimum versions tend to have
much slower resolve times (not to mention more error-prone) than those
who that do include minimum versions.


## needs-comment

Ever see a list of 20 requirements in a Rez package and you have no idea
if any of them are actually needed? Hopefully you'll never be in this
situation where you must refactor one of these packages. But if you are,
you'll be grateful for comments.

This checker is simple. If the Rez package defines at least one Python package,
``rez_lint`` ...

- finds every Rez package dependency based on the imported Python modules across all files
- gets a list of Rez packages from those imports
- checks this found list against the package's actual ``requires``

If there's any Rez package in ``requires`` that wasn't found from
Python imports, ``rez_lint`` errors, telling the user to add a comment
explaining why that dependency is there.

You can add a comment easily, using an in-line comment like this

```python
requires = [
	"dependency-1",  # I am an in-line comment
]
```

Or do a multi-line comment, starting from the line above the requirement
you're describing.

```python
requires = [
	# I am an multi-line comment
	# and there are multiple lines.
	#
	# Example:
	#     Formatting is also respected
	#
	"dependency-1",
]
```

You can also mix and match single-line and multi-line descriptions, if
you need to.


## no-change-log

The Rez package should have a CHANGELOG file at its root to explain what
has changed. It can be any file format

- CHANGELOG.rst
- CHANGELOG.md
- CHANGELOG.txt
- CHANGELOG.foo

If writing a Python package, it's recommended to use CHANGELOG.rst
though because it can then be added to Sphinx documentation
automatically.

Here's an example of the "Sphinx automatic import" feature.

A CHANGELOG written as .rst at a Rez package root
- https://github.com/ColinKennedy/sphinx-code-include/blob/master/CHANGELOG.rst

can then be included in Sphinx documentation, like this
- https://github.com/ColinKennedy/sphinx-code-include/blob/master/docs/changelog.rst

And here's a link to what the final result looks like
- https://sphinx-code-include.readthedocs.io/en/latest/changelog.html

Basically, you only need to maintain one file if you use the .rst
extension. But if you use any other extension, you have to maintain 2
separate CHANGELOG files.


## no-documentation

If the Rez package defines a Python package, that package is expected to
have Sphinx documentation. The documentation format that it checks for is
[in this Python code](https://github.com/ColinKennedy/rez_developer_packages/blob/07d92ddd15b3650f39c76387eb598ada64edd202/python_compatibility/python/python_compatibility/sphinx/conf_manager.py#L93-L130)

Basically to make documentation, run this

```sh
cd {package_root}
mkdir documentation
cd documentation
rez-env Sphinx -- sphinx-quickstart
```


## no-help

Every Rez package should have help documentation to link to.

You can use either a list-of-list-of-strs or a single str, as recommended by Rez's
[help attribute](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help)
That said, the list-of-list-of-strs form is recommended.

Here's an example of an excellent ``help`` attribute, for the "black" Python package.

```python
name = "black"

version = "19.10b0"

description = "The Uncompromising Code Formatter"

help = [
	["Developer Documentation", "https://black.readthedocs.io/en/stable"],
	["PyPI", "https://pypi.org/project/black/19.10b0"]  # Include version numbers whenever you can
	["Source Code", "https://github.com/psf/black"],
]
```

If you don't have documentation posted anywhere, feel free to just link
to a local file, such as a index.html or README.md in your Rez package.


```python
help = [
	["README", "README.md"],
]
```


## no-read-me

This one is simple. Every Rez package should have a README.md,
README.rst, or README.txt to explain what the package is for.

Really take some extra effort to flesh out details about the package. Such as:

- describe what the package does
- package requirements
- feature road map
- style guide information
- contributor guidelines

Explaining these topics a lot for new starters or people who stumble on the code.


## no-rez-test

Unless the Rez package is meant for configuration, chances are the
package implements some code. Your code should be tested, always. Define
tests using the package's
[test](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#tests)
attribute.


## no-uuid

For Rez, a UUID is its failsafe to make sure your package isn't
overwritten accidentally by another user. For example, say person A and
person B both make a package called "my_package" which have nothing to
do with each other. If B releases after A, all of the work A did could
be lost.

But if A and B both add UUIDs, when B releases their package, Rez will
prevent B's accidental release.

A UUID can be any string, but it's recommended to use an actual UUID so
there isn't a chance that 2 chosen UUIDs will ever accidentally be the
same.

### Create a UUID
```sh
python -c "import uuid;print(uuid.uuid4())"
```

### Add a UUID to your package
```python
name = "my_package"

# ... more package details ...

uuid = "3b65e850-dc18-4b1c-a2ba-1447c782673d"
```


## not-python-definition

Rez definition files should be package.py. Though other standards
exist, do not use them. For example, you could define a package using
package.yaml. If you're dealing with a code-base that uses package.yaml,
run ``rez-yaml2py`` and Rez will handle the conversion for you. You will
be better off using package.py files.


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

Also, if your requirements aren't sorted, sometimes you'll come across
packages that look like this:

```python
requires = [
	"rez-2+",
	"things_here-10",
	"more_examples-10",
	"you_get_the_point-13",
	"dependency_here-3.1+<5",
	"this_list_is_long-3",
	"so_people_dont-3.1",
	"actually_ready_it_that_much-4",
	"dependency_here-1.5+<5",
	"because_if_they_did-6",
	"theyd_see_that_a_dependency_were_listed_twice-4",
	"oops-1",
]
```

If they sorted the list above, it'd be plain as day that a requirement
was posted twice. In this case, "dependency_here" has 2 entries, when
there should only be one.

```python
requires = [
	"actually_ready_it_that_much-4",
	"because_if_they_did-6",
	"dependency_here-1.5+<5",
	"dependency_here-3.1+<5",
	"more_examples-10",
	"oops-1",
	"rez-2+",
	"so_people_dont-3.1",
	"theyd_see_that_a_dependency_were_listed_twice-4",
	"things_here-10",
	"this_list_is_long-3",
	"you_get_the_point-13",
]
```

Now from this list, it's obvious where the duplicate is and we can
remove it.

## semantic-versioning

The Rez documentation recommends
[semantic versioning](https://github.com/nerdvegas/rez/wiki/Basic-Concepts#versions).
So ``rez_lint`` also recommends it.


## too-many-dependencies

Having many dependencies in a Rez package is a strong indication that
the code can be restructured. It also limits the package's portability
and usefulness to others because anyone that uses a 10+ dependency
package is now, by extension, concerned with those dependencies.

If a package has many dependencies, it also means that it will break
if any those dependencies experience any problems.

If you are writing a package uses many dependencies, consider using
[Dependency Inversion](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
or [Dependency injection](https://en.wikipedia.org/wiki/Dependency_injection)
so that you can simply supply packages in the user's ``rez-env``
request instead of adding it directly into the Package. That will keep
dependencies down while still keeping packages flexible.


## url-unreachable

The rez-help command is determined by a written
[help attribute](https://github.com/nerdvegas/rez/wiki/Package-Definition-Guide#help)
in the Rez package.py.

This check makes sure that the URL still points to a valid URL or file
on-disk. If the help item is a URL and your Internet is down, the check
will not fail and instead pass-through. This is done so ``rez_lint``
won't accidentally tie up code from getting released due to a network
failure.


# TODO

- The requirements-related checks must take into account variants, not just the user's listed requirements.
