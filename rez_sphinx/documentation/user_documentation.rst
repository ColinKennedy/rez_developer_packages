..
    rez_sphinx_help:User Documentation

##################
User Documentation
##################

:ref:`rez_sphinx` is the bridge between `Rez`_ and `Sphinx`_. It takes all of
the `Sphinx`_'s great documentation-generation features and tightly integrates
it with `Rez`'s excellent environment management system. As a result, you get
documentation which is auto-configurable, auto-builds, and auto-links across
projects.

These documentation pages are resist `link rot`_, ensuring the pages you spent
time writing are built to last.

Check out the :ref:`beginner topics` below and, after that, consider reading
through :ref:`rez_sphinx commands`.


.. _beginner topics:

***************
Beginner Topics
***************

.. toctree::
   :maxdepth: 1

   What Is Rez Sphinx <what_is_rez_sphinx>
   why_use_rez_sphinx
   features
   getting_started


.. _rez_sphinx commands:

************
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


***************
Advanced Topics
***************

These pages, in no particular order, explain how to customize :ref:`rez_sphinx`
to suit your projects. It's aimed towards people who want better documentation
customization or are administering :ref:`rez_sphinx` at a company / studio.

.. toctree::
   :maxdepth: 1

   using_sphinx_rtd_theme
   adding_extra_interlinking
   configuring_rez_sphinx
   auto_append_help_tags
   enable_external_website_publishing
   enabling_rez_help_integration
   rez_sphinx_as_a_release_hook
   batch_publish_documentation
   linking_rez_sphinx_with_other_documentation_tools
