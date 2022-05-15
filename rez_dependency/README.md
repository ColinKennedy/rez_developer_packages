# rez_dependency

A CLI for querying the dependencies of a Rez package.

Rez has an existing command,
[rez-depends](https://github.com/nerdvegas/rez/wiki/Command-Line-Tools#rez-depends)
which is great at answering the question "Is my package used by other packages
and, if so, where?"

In contrast, `rez_dependency` answers the question "What packages does my
package depend upon, if any?"


## Comparison To rez-env
If you just need a one-off list of runtime requirements of a package, you can
always just run `rez-env` and use its printed output to get a rough list
of dependencies.

```
$ rez-env Qt.py PySide2

You are now in a rez-configured environment.

requested packages:
Qt.py
PySide2
~platform==linux      (implicit)
~arch==x86_64         (implicit)
~os==CentOS-7.9.2009  (implicit)

resolved packages:
PySide2-5.15.1      ~/packages/PySide2/5.15.1/4a6f3de111fa67242e2de08e54b1bfde4db8ae88
Qt.py-1.3.6         ~/packages/Qt.py/1.3.6/c90100464e7464b53ef2d620102d65c024615d9e
arch-x86_64         ~/packages/arch/x86_64
os-CentOS-7.9.2009  ~/packages/os/CentOS-7.9.2009
platform-linux      ~/packages/platform/linux
# ... more packages ...
```

But if you want ...

- package requests, not just the resolved versions
- to gather `private_build_requires` / `build_requires` dependencies
- output as a tree, not just a list
- pretty-ified output

Then `rez_dependency` is for you.


## How To Run
### levels
```sh
rez_dependency list 'package_request-1.2+<3'
```

Prints a `rez-depends`-list output:

```
#0: package_request
#1: a_dependency python
#2: another_nested_dependency
#3: python
```

### list
```sh
rez_dependency list 'package_request-1.2+<3'
```

Prints each Rez package family, in alphabetical order

```
a_dependency
another_nested_dependency
package_request
python
```

### tree
```sh
rez_dependency tree 'package_request-1.2+<3'
```

Prints the full tree, in the order that dependencies are found.

```
package_request:
    a_dependency:
        another_nested_dependency:
            python
    python
```


## Options
All commands will show `requires` and `variants` (if applicable). If you want
to include `build_requires` or `private_build_requires` in the ouput, use
`--build-requires` / `--private-build-requires`.

### tree
`--display-as` allows you to output a JSON tree, if desired.

```sh
rez_dependency tree 'package_request-1.2+<3'
```

```
{
    "package_request": {
        "a_dependency": {
            "another_nested_dependency":
                "python": {}
            }
        },
        "python": {}
    }
}
```
