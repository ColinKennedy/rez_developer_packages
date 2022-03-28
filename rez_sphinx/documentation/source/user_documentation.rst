..
    rez_sphinx_help:User Documentation

.. _rez_sphinx:

##################
User Documentation
##################

TODO : Visit this tutorial once rez_docbot exists. And possibly update it with
remote information.

Welcome to ``rez_sphinx``, the missing link between `Rez`_ and `Sphinx`_.
``rez_sphinx`` automatically initializes, interlinks, configures, and builds
documentation in your Rez packages. It even links to **other** Rez packages if
they also have documentation. ``rez_sphinx`` does all this so you can do what
you want to do, faster. Which is writing good docs!

TODO : Make this rez_docbot link work

``rez_sphinx`` is also a plug-in for :ref:`rez_docbot
<rez_docbot:user_documentation>` The documentation below mostly just goes over
``rez_sphinx`` on its own but may mention it from time to time.


Beginner Topics
***************

.. toctree::
   :maxdepth: 1

   why_use_rez_sphinx
   getting_started


All Commands
************

:ref:`rez_sphinx` has a number of commands which make working with
documentation easier.

.. toctree::
   :maxdepth: 1

   build <build_command>
   config <config_command>
   init <init_command>
   publish <publish_command>
   suggest <suggest_command>
   view <view_command>


Advanced Topics
***************

These pages, in no particular order, explain how to customize :ref:`rez_sphinx`
to suit your projects. It's aimed towards people who want better documentation
customization or are administering :ref:`rez_sphinx` at a company / studio.

.. toctree::
   :maxdepth: 1

   using_sphinx_rtd_theme
   adding_extra_interlinking
   publishing_your_documentation
   configuring_rez_sphinx
   auto_append_help_tags
   linking_rez_sphinx_with_other_documentation_tools
