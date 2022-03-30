.. _rez_sphinx tag:

#####################
Auto-Append Help Tags
#####################


:ref:`rez_sphinx` is capable of auto-connecting dependency packages together.
However, this functionality isn't enable by default. It has to be configured
but it's easy and only needs to be done once.


Configuring auto-help linking
*****************************

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
You can double-check that by running :ref:`rez_sphinx view publish-url`.


Adding Documentation Automatically
**********************************

By default, the :ref:`default file entries`, ``user_documentation`` and
``developer_documentation`` are added to your package.py `help`_ attribute each
time the Rez package is built using `rez-build`_.

If you want to add other files to the `help`_ during `rez-build`_,

you've got two options:

- Let :ref:`rez_sphinx` add your files for you
- Define the paths to the files manually.


.. _automated_auto_help_appending:

Let :ref:`rez_sphinx` write to ``help`` for your
================================================

Simply add this snippet into any of your .rst files:

::

    ..
        rez_sphinx_help:Optional Label


Including "rez_sphinx_help:Optional Label" adds this to your `help`_ attribute
on-build:

.. code-block:: python

   help = [
       ["Existing documentation", "README.md"],
       ["Optional Label", "{root}/file_path.html"],
   ]

And later the {root} gets replaced by your publisher documentation URL, using
``view_url``.

The found "Optional Label" logic goes like this:

- If there's a label defined after like ``rez_sphinx_help:Foo``, use it
- If not, get the current file's header text
- If no found header, use the file's name, instead.


Write the .html, yourself
=========================

You can always write the path to the .html that your .rst files generates by-hand.

.. code-block:: python

   help = [
       ["Existing documentation", "README.md"],
       ["Hand Written Entry Here", "{root}/file_path.html"],
   ]

If you have a .rst file located at ``{rez_package_root}/documentation/file_path.rst``,
then you'd want to write ``"{root}/file_path.html"``.

This isn't super recommended though because what if you move, rename or delete
your file_path.rst file later? Then the next time documentation builds, ``Hand
Written Entry Here`` will point to nothing. It's better to use the automated
:ref:`automated_auto_help_appending` method, instead.
