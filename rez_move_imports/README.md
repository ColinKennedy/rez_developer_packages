rez_move_imports is a very basic tool. It deals with a very
"Rez-specific" problem. When you have a Rez package that's been
deprecated, or Python files that have been moved, how do you actually
refactor the packages that import and move everything?

Sure, you can do it manually. But imagine a mature code-base with
hundreds of packages.

rez_move_imports was designed for exactly this purpose. And when
combined with automation tools such as rez_batch_process, it becomes a
fully automated way to batch-replace Rez packages.


## How To Run

```sh
rez-env rez_move_imports -- python -m rez_move_imports . --namespaces foo,another --requirements some_package_another-2+<3,another --deprecate old_package_foo,foo
```

These options aren't as complicated as they seem, basically, if read like a sentence, the previous command means

From the current directory of some Rez package
- Replace all imports "foo" with "another" 
- If there are no more "foo" imports, remove "old_package_foo" from the list of dependencies of the Rez package in the current directory
- If any imports are replaced with "another", add "some_package_another-2+<3" as a new dependency for the Rez package in the current directory


## Checking for multiple namespaces before deprecating
If your "old_package_foo" package has more than one root namespace, just append more commas

```sh
rez-env rez_move_imports -- python -m rez_move_imports . --namespaces foo,another --requirements some_package_another-2+<3,another --deprecate old_package_foo,foo,something_else,more.namespaces
```

This one means the exact same thing as before but instead we're saying
"in order to deprecate old_package_foo as a dependency, every import
namespace listed, 'foo', 'something_else', and 'more.namespaces' must
all be completely removed from the current Rez package"


## Adding more than one requirement using 1-or-more namespaces
Basically, the namespaces listed in "--deprecate" is an AND operation
- all of the namespaces must be removed before "old_package_foo"
is removed. In contrast, "--requirements" is an OR operation. If
**any** import is replaced by one of the namespaces listed there,
"some_package_another-2+<3" will be added as a requirement.

You can also expand the number of namespaces with extra commas, just like "--deprecate".


## About --namespaces
In many cases, this flag will end up being concise and simple. But
it also supports an extensive syntax. See the documentation for
[move_break](../move_break) for more information.


# How To Automate
By itself, rez_move_imports only works with single Rez packages. But
wrap it into a rez_batch_process command and suddenly you've got a tool
that can automatically manage imports + dependencies of all of your Rez
packages.

TODO add an example command here.

# TODO
- Update the command examples here
- Need unittests of the command-line

- allow list of old packages to "replace"
- their list of replacements
- namespaces to replace
- directory to start from

