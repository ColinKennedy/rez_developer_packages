``rez_pip_boy`` is a small wrapper around [rez-pip](https://github.com/nerdvegas/rez/blob/a9f61980a9cebcf67df09023cccdcbf1b9edea66/wiki/pages/Pip.md).

(rez_pip_boy comes from the name "Pip-Boy 2000", a reference to the game Fallout)

If you're working with a pipeline that natively supports rez-pip then
definitely use that. But if you desire a way to build and modify Rez-pip
packages as a "source" Rez package then ``rez_pip_boy`` may help.

Also note: The Rez team has a road-map item for making
repository locations for Rez packages, described
[in this issue](https://github.com/nerdvegas/rez/issues/673).
If it is implemented, it'll basically deprecate the need for
``rez_pip_boy`` completely. But in the meantime, something else needs to
fill the gap.

## How To Run

```sh
export PIP_BOY_TAR_LOCATION=/somewhere/to/save/any/generated/tar_files
python -m rez_pip_boy install six==1.14.0 --install-directory "/tmp/some_packages_path" --python-version=2.7 --no-dependencies --verbose
```

The stuff in ""s is anything you'd normally write to rez-pip.
The /tmp/output_location is where your final Rez package.py files will
end up.


## How It Works

- ``rez_pip_boy`` downloads a variant of the pip package and archives it into a .tar.gz file
- It then makes a build script which targets + uncompresses that file
- The tar is copied to an archive folder
- Your generated package.py gets copied to a folder of your choice

And that's pretty much the full tool.

It's important to understand that ``rez_pip_boy`` must be run
per-variant of any pip package you want to install. For example, it
doesn't try to guess which Python versions you want to install for
a package. Just like regular ``rez-pip``. You have to provide that
information.
