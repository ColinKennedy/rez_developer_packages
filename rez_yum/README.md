`rez-yum` allows Rez users to download RPMs from online and install them
recursively. It works just like `rez-pip` in that it creates installed Rez
packages. If you're familiar with `rez-pip`, you'll generally understand how to
use this.


## Getting Started
TODO


## Example Commands
### A Basic Install
Install [gcc](https://rpmfind.net/linux/rpm2html/search.php?query=gcc) and all
of its dependencies.

```sh
rez-yum install gcc
```

You can also control where on-disk the packages will end up. If no destination
is given, the default Rez `rez-config local_packages_path` is used instead.

```sh
rez-yum install gcc --destination /some/path
```

## Converting
If you have a RPM that you want to make into a Rez package, `rez-yum` has a
command for that.

Just note that the following caveats apply:

TODO check terminology here

- The RPM is expected to be a compiled RPM, not a source RPM
- If the RPM depends on other RPM packages, that dependency management is not
  handled by `rez-yum`. You'd have to download and convert those on your own.

```sh
rez-yum convert /path/to/file.rpm --destination /some/path
```

The command above makes a Rez package.py + the RPM, starting from /some/path
