## Provides - Interesting Mechanic
https://rpm-software-management.github.io/rpm/manual/dependencies.html

Provides can be added to packages so they can be referred to by dependencies other than by their name. This is useful when you need to make sure that the system your package is being installed on has a package which provides a certain capability, even though you don’t care what specific package provides it. For example, sendmail won’t work properly unless a local delivery agent (lda) is present. You can ensure that one is installed like this:

    Requires: lda

This will match either a package called lda (as mentioned above), or any package which contains:

    Provides: lda

## Versioning syntax
https://rpm-software-management.github.io/rpm/manual/dependencies.html

`[epoch:]version[-release]`

```
epoch   (optional) number, with assumed default of 0 if not supplied
version (required) can contain any character except '-'
release (optional) can contain any character except '-'
```

Requires: perl >= 9:5.00502-3

Unspecified epoch and releases are assumed to be zero, and are interpreted as
"providing all" or "requiring any" value.

The release tag is usually incremented every time a package is rebuilt for any
reason, even if the source code does not change. For example, changes to the specfile, compiler(s) used to build the package, and/or dependency changes should all be tracked by incrementing the release.
 - !!! It sounds like I need to keep in mind the release number as well, in that case.


## Scriptlet Dependencies
Scriptlet Dependencies

Often package scriptlets need various other packages in order to execute correctly, and sometimes those dependencies aren’t even needed at runtime, only for installation. Such install/erase-time dependencies can be expressed with “Requires(): " notation, for example the following tells rpm that useradd program is needed by the package %pre scriptlet (often the case if a package uses a custom group/username for its files):

        Requires(pre): /usr/sbin/useradd

!! Sounds like a build_requires to me. Not sure if that will matter since we're using installed RPM packages


## Automatic Dependencies
Automatic Dependencies

To reduce the amount of work required by the package builder, RPM scans the file list of a package when it is being built. Any files in the file list which require shared libraries to work (as determined by ldd) cause that package to require the shared library.

For example, if your package contains /bin/vi, RPM will add dependencies for both libtermcap.so.2 and libc.so.5. These are treated as virtual packages, so no version numbers are used.

!!! So that explains the file paths to paths on-disk. I can probably ignore these. The host OS would provide them.
 - !!! TODO maybe It may be useful to something in `commands()` which checks to make sure those paths exist though!!!


## Interpreters and Shells

Modules for interpreted languages like perl and tcl impose additional dependency requirements on packages. A script written for an interpreter often requires language specific modules to be installed in order to execute correctly. In order to automatically detect language specific modules, each interpreter may have its own generators. To prevent module name collisions between interpreters, module names are enclosed within parentheses and a conventional interpreter specific identifier is prepended:

  Provides: perl(MIME-Base64), perl(Mail-Header)-1-09

  Requires: perl(Carp), perl(IO-Wrap) = 4.5

!!! That explains the ()s. I wonder how I should handle those


## Build dependencies

The following dependencies need to be fullfilled at build time. These are similar to the install time version but these apply only during package creation and are specified in the specfile. They end up as “regular” dependencies of the source package (SRPM) (BuildRequires? become Requires) but are not added to the binary package at all.

    BuildRequires:
    BuildConflicts:
    BuildPreReq:

Again, I probably don't need to have these


## "Soft" Dependencies
!!! Look into what these are and how they're used.

https://rpm-software-management.github.io/rpm/manual/tags.html

Soft dependencies
