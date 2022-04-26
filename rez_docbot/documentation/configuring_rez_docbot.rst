######################
Configuring rez_docbot
######################

rez_docbot allows users to define multiple publish locations for documentation
through configuration settings. The exact details of "what settings are allowed
in each configuration" depends on the publisher. However, everything in this
page is supported by all publisher types. If you want to read about
per-publisher details, check out :doc:`publisher_types`.

In general, users can define configuration settings in 1 of 2 ways:

- Globally, for all packages
- :ref:`per-package configuration`


**************
Configurations
**************

These are the general, customizable settings for :ref:`rez_docbot`. They affect
anything from publish behavior, what folders end up getting written to disk,
and where publish data is made available.


.. _rez_docbot.publishers:

rez_docbot.publishers
=====================

This setting is where you define all publish destinations for documentation.
You are free to create 1 or more publishers and each destination will be
published to. Most of the time, users will only define a single publisher.
However if you do make more than one publisher, note that the first publisher
is special and the other publishers are considered fallbacks / redundancy
publishers.

In short, if you make more than one publisher, always place the most important
publisher first.

TODO : write configuration here

This simple configuration has tons of variety - you can dynamically create and
generate documentation repositories per Rez package, or a mono-documentation
repository containing all Rez packages, etc etc. Check out
:doc:`popular_publish_configurations` to learn the different ways
configurations can be set up.


rez_docbot.publishers.*.commit_message
======================================

TODO


rez_docbot.publishers.*.latest_folder
=====================================

TODO if set to an empty string, no latest folder is made


.. _publish_pattern:

rez_docbot.publishers.*.publish_pattern
=======================================

_get_resolved_publish_pattern

TODO

.. seealso::

    :func:`.get_first_versioned_view_url`

See :doc:`publishing_per_version` for details


rez_docbot.publishers.*.relative_path
=====================================

TODO


rez_docbot.publishers.*.repository_uri
======================================

TODO


rez_docbot.publishers.*.required
================================

TODO


rez_docbot.publishers.*.skip_existing_version
=============================================

TODO

rez_docbot.publishers.*.version_folder
======================================

TODO


rez_docbot.publishers.*.view_url
================================

``view_url`` is the URL (or directory on-disk) is where documentation is
expected to be viewed.

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "repository_uri": "git@github.com:FakeUser/{package.name}",
                    "view_url": "https://www.FakeUser.github.io/{package.name}",
                    # ... more settings ...
                },
            ],
        },
    }

In a typical documentation set up, you typically would push documentation to a
remote location, like ``"git@github.com:FakeUser/{package.name}"`` but then
that documentation is viewable to the average user at
``https://www.FakeUser.github.io/{package.name}"``.

.. important::

    Tools such as :ref:`rez_sphinx:rez_sphinx` rely on this URL being accurate
    in order to link Sphinx documentation to Rez. This is done via the
    :func:`.get_first_versioned_view_url`. In short, absolutely make sure this
    setting is accurate!


.. _per-package configuration:

*************************
Per-Package Configuration
*************************

All settings can be
TODO Finish
