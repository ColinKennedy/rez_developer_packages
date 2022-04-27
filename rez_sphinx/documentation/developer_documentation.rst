#######################
Developer Documentation
#######################

..
    rez_sphinx_help:Developer Documentation

This page is for people who are interested in how :ref:`rez_sphinx` ticks.
It's a pretty simple tool but there's a couple places that deserve extra
attention because there's a bit complex or assume things about the user's
environment.

Broadly speaking, the most important parts of any Package / rez_sphinx set up are.

- The :doc:`generated conf.py file <how_rez_and_sphinx_are_linked>`
- The :mod:`.preprocess_entry_point` module, which is used to make auto-help
  :doc:`auto_append_help_tags` work
- Understanding the fact that :ref:`rez_sphinx` has no publishing capabilities
  by default and instead delegates all of that work to an optional dependency,
  :ref:`rez_docbot`.
- TODO Add details once we have a release plugin. Describe that here.

  - Also make a second page specifically explaining how the release plugin
    works and how to set that up



.. toctree::
    :maxdepth: 1

    how_rez_and_sphinx_are_linked
    how_interlinking_works
