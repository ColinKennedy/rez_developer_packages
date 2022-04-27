######################
How interlinking works
######################

As mentioned in :doc:`adding_extra_interlinking`, it's possible for any Rez package
to refer to the documentation in another Rez package automatically.

Every time a documentation project is built, Sphinx creates an
:ref:`objects.inv` file. This is true not just for :ref:`rez_sphinx` but any
Sphinx-built documentation. Even Python's documentation works the same way. If
you visit
[https://docs.python.org/3/objects.inv](https://docs.python.org/3/objects.inv),
it'll directly download objects.inv to your machine. :ref:`rez_sphinx build
run` takes advantage of this file to do the interlinking.

Any Rez package built with ``rez-sphinx`` exports the location of your
"objects.inv" file so that other Rez packages may use it. And any Rez package
whose dependencies have an "objects.inv" are automatically cross linked, using
`sphinx.ext.intersphinx`_. And that's the basis for how ``rez-sphinx`` works.
All other features are basically to just enhance the user experience.

For more details on how ``rez-sphinx`` internals works, see
:doc:`rez_sphinx_internals`. Otherwise, head over to :doc:`getting_started` to
try ``rez-sphinx`` for yourself!
