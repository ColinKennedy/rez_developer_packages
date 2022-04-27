########
Features
########

But above all else, rez_sphinx is **thorough** and well tested. `Sphinx`_ does
an incredible job making documenting Python code easier but it just isn't able
to ensure documentation is kept up-to-date or link to existing documentation
reliably.

rez_sphinx makes your documentation built to last. Here's a summary of some of
the features that :ref:`rez_sphinx` has to offer.


*************
Base Features
*************

- :ref:`Auto-initialize documentation <rez_sphinx init>`

    - Supports combined or separate source / build folders
    - Extends ``sphinx-quickstart`` with :ref:`optional, template files
      <rez_sphinx.init_options.default_files>`
    - :ref:`Batch-publish documentation <batch_publish_documentation>` for source
      **or** installed Rez packages

        - :ref:`CLI-based utilities <rez_sphinx suggest build-order>` to ensure "best results"

- :ref:`API documentation auto-generation / auto-syncing <rez_sphinx build run>`
- :ref:`Validate missing documentation
  <rez_sphinx.init_options.check_default_files>`, pre-build
- Extremely configurable :doc:`configuring_rez_sphinx` and :ref:`publisher
  settings <rez_docbot:customization>`

    - CLI-based :ref:`configuration inspector <rez_sphinx config>` - shows "unresolved" values
    - CLI-based :ref:`"actual, resolved values" inspector <rez_sphinx view>`


******************
Intrinsic Features
******************

- :doc:`Auto-link and cross reference documentation
  <enabling_rez_help_integration>` from multiple Rez packages at once

    - This works ...

        - :ref:`Even if package is external
          <rez_sphinx.intersphinx_settings.package_link_map>` and you don't
          want to change it.

            - Example: `rez-pip`_ installed packages.

        - :doc:`Even if that Rez package isn't build with rez_sphinx
          <linking_rez_sphinx_with_other_documentation_tools>`

- Auto-discovers your documentation and :ref:`integrates them into rez-help
  <enabling_rez_help_integration>`
- Provides a default :ref:`build_documentation rez-test command <rez_sphinx
  init>`, for easier documentation building.
- :ref:`rez_sphinx` provides sensible `Sphinx conf.py`_ values for your Sphinx projects

    - But you can still :ref:`override the conf.py customizations <how to
      override rez_sphinx conf.py>` with whatever you'd like


***************
Opt-In Features
***************

Opt-In Themes
=============

You can set all Rez packages using :ref:`rez_sphinx` to use sphinx_rtd_theme
(or whichever theme you prefer), using :doc:`this Sphinx theme tutorial
<using_sphinx_rtd_theme>`.


Opt-In Publishing
=================

:ref:`rez_sphinx` can auto-publish your documentation.

It supports this using a :ref:`release_hook <rez_sphinx_as_a_release_hook>`.

As a publisher, :ref:`rez_sphinx publish run` provides these features:

- One-to-many repositories-to-Rez package support - :ref:`Multiple Rez packages in a
  single repository <rez_docbot:multi_package_publishing>`
- One-to-one repository-to-Rez package support - :ref:`One package per
  repository <rez_docbot:mono_package_publishing>`
- :ref:`"latest live" documentation <rez_docbot:latest_documentation>`
  which auto-updates with each new version
- :ref:`Versioned, locked documentation <rez_docbot:versioned_documentation>`

    - :doc:`Auto-linked and cross referenced documentation
      <enabling_rez_help_integration>` links against the versioned
      documentation. The result - links to external documentation don't go out
      of date.
