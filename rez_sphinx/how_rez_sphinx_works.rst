====================
How rez-sphinx Works
====================

Every time a documentation project is built, Sphinx creates an "objects.inv"
file. This is true not just for Rez but any Sphinx-built documentation. Even
[Python's documentation works the same way](https://docs.python.org/3/objects.inv).

Any Rez package built with ``rez-sphinx`` exports the location of your
"objects.inv" file so that other Rez packages may use it. And any Rez package
whose dependencies have an "objects.inv" are automatically cross linked, using
`https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
<sphinx.ext.intersphinx>`_. And that's the basis for how ``rez-sphinx`` works.
All other features are basically to just enhance the user experience.

For more details on how ``rez-sphinx`` internals works, see
:doc:`rez_sphinx_internals`. Otherwise, head over to :doc:`getting_started` to
try ``rez-sphinx`` for yourself!
