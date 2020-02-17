A simple Rez Python package that can replace Python imports.

Its syntax works like this:

As long as you have the namespace of a module's before and after location, this script can be run on any module.

``move_break`` uses static analysis, so it doesn't need an environment to
import Python modules. As long as the module doesn't have syntax errors,
just point ``move_break`` to the file or folder and it will work like a
charm, every time.


## From API

```python
from move_break import move_break_api

files = {"/path/to/some/folder/or/file.py"}
namespaces = [("old.namespace", "some_new.namespace")]
move_break_api.move_imports(files, namespaces, partial=True)
```

Pretend that "file.py" has content like this:

```python
from old import namespace
from old.namespace import stuff
import old.namespace
```

After running `move_imports`, it will now look like this


```python
from some_new import namespace
from some_new.namespace import stuff
import some_new.namespace
```

And that's pretty much it.

Of course, ``move_imports`` works with complicated imports, indentation,
and lexs Python files so you already get the correct result. This is
just a simple example.


## From Command-Line
From the previous section, the equivalent CLI command looks like this:

```sh
python -m move_break "/path/to/some/folder/or/file.py" old.namespace,some_new.namespace
```

## Note

It's recommended to not use "partial" / "partial-matches" whenever
possible. We just did it earlier just to keep the examples simple.

Using partial is only recommended if you either

A. Know for a fact that a new namespace contains all of the child modules / functions / classes of a previous namespace
B. You're unable to provide a full list of namespaces to find and replace.

So instead of relying on "partial", try to define enough dotted
namespaces for your imports to be replaced.

In the previous sections, the "non-partial" versions look like this:

```python
from move_break import move_break_api

files = {"/path/to/some/folder/or/file.py"}
namespaces = [
	("old.namespace", "some_new.namespace"),
	("old.namespace.stuff", "some_new.namespace.stuff"),
]
move_break_api.move_imports(files, namespaces, partial=True)
```

```sh
python -m move_break "/path/to/some/folder/or/file.py" "old.namespace,some_new.namespace\nold.namespace.stuff,some_new.namespace.stuff"
```

It's more work to set up without "partial" but at least then you'll know
that you're getting exactly what you expect. Using "partial" always has
a potential to produce good substitutions but replaces more imports than
you may have meant to.


# TODO : Add unittests that checks for bad arguments
- Need unittest to make sure the CLI works
 - There needs to be a unittest that reads namespaces as text
 - another that reads from process substitution
 - another that reads from file paths.

-  Add an option to allow namespace endings to be aliased (if the tail doesn't match the original)
 - e.g. [("foo.bar", "thing.other")]
  - "from foo import bar" would be come "from thing import other as bar"
  - instead of "from thing import other"
  - this is for ultra-conservative people who want to make sure code doesn't break
