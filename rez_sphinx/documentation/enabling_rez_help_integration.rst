.. _rez_sphinx tag:

#############################
Enabling rez-help Integration
#############################

TODO : Re-structure this based on the release hook. Compare / Contrast both methods

:ref:`rez_sphinx` is capable of auto-connecting dependency packages together.
However, this functionality isn't enabled by default. It has to be configured
but it's easy and only needs to be done once.

There's 2 methods of doing this, each have their own pros / cons

- :ref:`adding_rez_sphinx_as_a_release_hook`
- :ref:`adding_rez_sphinx_as_a_preprocess`

Between the two, :ref:`adding_rez_sphinx_as_a_release_hook` is the preferred
way of working because it handles not just auto-appending but also automatic
documentation publishing.

To summarize the two differences:

:ref:`adding_rez_sphinx_as_a_release_hook`

Pros:

- Executes quickly
- Is stackable with other release hooks

Cons:

- Doesn't run during `rez-build`_.

    - This can be mitigated with the :ref:`rez_sphinx view package-help` command.


:ref:`adding_rez_sphinx_as_a_preprocess`

Pros:

- Runs during `rez-build`_

Cons:

- Runs during other Rez commands, even `rez-test`_ and others
- Tends to slow down Rez overall and can be quite spammy
- `package_preprocess_function`_ isn't stackable. So if you already use that in
  your pipeline, this option would overwrite your existing function.

In short, if you value "correctness" and are fine with waiting a bit longer,
:ref:`adding_rez_sphinx_as_a_preprocess` is best. However if you only really
care about `help`_ being correct on-release and want Rez to be as fast as
possible, :ref:`adding_rez_sphinx_as_a_release_hook` is for you.


*****************************
Configuring auto-help linking
*****************************

.. _adding_rez_sphinx_as_a_release_hook:

Adding rez_sphinx as a release hook
===================================

TODO : Write this later

Once you've built :ref:`rez_sphinx`, you'll want to add the following to your
`rezconfig.py`_.

.. code-block:: python

    plugin_path = [
        "/path/to/your/installed/rez_sphinx/1.0.0/python-3/python/rez_sphinx_plugins",
    ]
    release_hooks = ["publish_documentation"]

Whenever you `rez-release`_ a Rez package, if it has :ref:`rez_sphinx`
documentation, the `help`_ attribute will get auto-appended to, based on what
:ref:`rez_sphinx` can find.

.. note::

    The :ref:`rez_sphinx view package-help` command lets you see help
    :ref:`rez_sphinx` will modify your package's `help`_ attribute, prior to
    releasing.  If you want to customize the output paths / order / etc,
    there's a number of options such as :ref:`rez_sphinx.auto_help.filter_by`
    and :ref:`rez_sphinx.auto_help.sort_order`.


.. _adding_rez_sphinx_as_a_preprocess:

Adding rez_sphinx as a preprocess
=================================

Once you've built :ref:`rez_sphinx`, you'll want to add the following to your
`rezconfig.py`_.

.. code-block:: python

    package_definition_build_python_paths = [
        "/path/to/your/installed/rez_sphinx/1.0.0/python-3/python/rez_sphinx/preprocess",
    ]
    package_preprocess_function = "preprocess_entry_point.run"


Now whenever you build a Rez package, if it has :ref:`rez_sphinx`
documentation, the `help`_ attribute will get auto-appended based on what
:ref:`rez_sphinx` can find.

If you only plan to publish documentation locally, you can skip the next
section.  However if you want to **publish** your documentation (to your
network or on the Internet), you need an extra plug-in called ``rez_docbot``,
which is explained in the next section.


Adding rez_docbot as a preprocess
=================================

``rez_docbot`` is a documentation publisher tool for Rez. There's a page called
:ref:`rez_docbot:getting_started` which can help get you set up. Just in case
that page goes down, I'll summarize the steps here:

.. important::

    These steps assume you're using `GitHub Pages`_ (or GitHub Enterprise).
    If you want to see **other** set-ups, :ref:`rez_docbot:getting_started`
    goes over those in-depth.

Add this to your `rezconfig.py`_:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {
                        "user": "YourUserName",
                        "token": "some_access_token_here",
                        "type": "github",
                    },
                    "branch": "gh-pages",
                    "repository_uri": "git@github.com:SomeUserOrOrganization/{package.name}",
                    "view_url": "https://SomeUserOrOrganization.github.io/{package.name}",
                },
            ],
        }
    }

The important details are:

- The ``view_url`` is what will be auto-added into your Rez package.py `help`_
  attribute. Make sure it's correct!
- You can publish your documentation to multiple places. However only the first
  found publisher is used during the auto-help generation step. So again, make
  sure the first publisher's ``view_url`` is correct!
- You don't have to hard-code an access token into your config, since that's
  not great OpSec. Again, see :ref:`rez_docbot:getting_started` to learn how to
  do that.

Once you've added that, your rez_docbot configuration should be reading properly.
You can double-check that by running :ref:`rez_sphinx view view-url`.
