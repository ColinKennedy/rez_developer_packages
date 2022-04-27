.. _user_documentation:

##################
User Documentation
##################

This page and :doc:`developer_documentation` page are fairly similar
because the users typically are other developers. :doc:`developer_documentation`
goes into details on how rez_docbot works as well as administering it.

The user documentation section just describes what ``rez_docbot`` does
and how to set it up.

.. toctree::
    :maxdepth: 1

    installation
    getting_started
    publisher_types


.. _rez_docbot:

**********
rez_docbot
**********

..
    rez_sphinx_help:User Documentation

``rez_docbot`` is a simple documentation publisher. It takes generated
documentation, usually .html files or a directory, and pushes them to a remote
destination like `GitHub`_.

Beyond that, this tool doesn't do all that much. It comes with lots of
:doc:`configuration options <configuring_rez_docbot>`, but most users
will never need to touch them.

``rez_docbot`` is usually included as a plug-in to another too, like
:ref:`rez_sphinx`. Effectively, it gives :ref:`rez_sphinx` publishing
capabilities which it normally would not be able to do.

Check out :doc:`getting_started` to learn more.

.. note::

    To learn how to administer ``rez_docbot`` to a pipeline, see
    :doc:`developer_documentation`.
