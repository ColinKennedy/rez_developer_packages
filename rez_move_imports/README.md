rez_move_imports is a very basic tool that deals with a very
"Rez-specific" problem. Imagine you need to move modules from one Rez package 
to another, or a class or function or whatever. Traditional Python refactoring
tools aren't going to cut it in many cases, especially when each Rez package
lives in a separate git repository.

How do you actually refactor these Rez packages and move everything reliably?

Sure, you can do all the moving and renaming manually. But that's prone
to human error, is really time consuming, and in a big Rez code-base -
basically impractical.

rez_move_imports was designed to automate refactoring Rez python
packages. And when combined with automation tools such as
[rez_batch_process](../rez_batch_process), it becomes a fully automated
way to batch-replace Rez packages.


## How To Run

```sh
rez-env rez_move_imports -- python -m rez_move_imports ". foo,another --partial" --requirements some_package_another-2+<3,another --deprecate old_package_foo,foo
```

These options aren't as complicated as they seem, basically, if read
like a sentence, the previous command says

From the current directory of some Rez package
- Replace all Python imports "foo" with "another".
- If, after the replacement, there are no more imports that still refer to "foo",
  remove the Rez package called "old_package_foo" from the list 
  of required packages because it's been deprecated.
    - The Rez package.py in your current working directory is the one that gets modified.
- If any imports are replaced with "another", 
  add "some_package_another-2+<3" as a new dependency.


## Checking For Multiple Namespaces Before Deprecating
Of course, if you have a complicated Rez package that defines more than
one Python namespace, you can handle all that too. Just add more commas.

```sh
rez-env rez_move_imports -- python -m rez_move_imports ". foo,another --partial" --requirements some_package_another-2+<3,another --deprecate old_package_foo,foo,something_else,more.namespaces
```

This one means the exact same thing as before but instead we're saying
"in order to deprecate "old_package_foo" as a dependency, every import
namespace listed, "foo", "something_else", and "more.namespaces" must
all be completely removed from the current Rez package. But if any
one of those namespace are still around, don't deprecate "old_package_foo"."


## Adding More Than One Requirement Using 1-or-more Namespaces
Basically, the namespaces listed in "--deprecate" is an AND operation.
All of the namespaces must be removed before "old_package_foo"
is removed. In contrast, "--requirements" is an OR operation. If
**any** import is replaced by one of the namespaces listed there,
"some_package_another-2+<3" will be added as a requirement to the
current Rez package.

You can also expand the number of namespaces of "--requirements" with
extra commas, just like how you do with "--deprecate".


## Understanding The Arguments
The arguments passed to `rez_move_imports` can be split into 2 groups.

- The stuff in ""s
- Everything else

In the example commands above, the text inside ""s get passed directly to
another API, called [move_break](../move_break). Any argument that move_break
supports can be used here.

The remaining arguments outside of the ""s are all things that
`rez_move_imports` expects.


## Caveats
- This package assumes that you've defined your Rez package as a package.py file.


# How To Automate
By itself, rez_move_imports only works with single Rez packages. But
wrap it into a rez_batch_process command and suddenly you've got a tool
that can automatically manage imports + dependencies of all of your Rez
packages.


# TODO
- Update the command examples here. commands for this + a command for rez_batch_process

- add an option to NOT bump the Rez package after making the needed changes
