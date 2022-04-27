###############
Getting Started
###############

*******************
Run rez_sphinx init
*******************

To link :ref:`rez_sphinx` with your Rez package, here's what you must do:

::

    cd /directory/to/source/your_package_name_here
    rez-env your_package_name_here rez_sphinx -- rez_sphinx init

That's it. This command only needs to be ran **once**.


*************
Run rez_build
*************

You're now ready to build your documentation. :ref:`rez_sphinx` made some
changes to your `package.py`_ file so before continuing be sure to run
``rez-build`` just once more.

::

   rez-build --clean --install


************************
Write Some Documentation
************************

:ref:`rez_sphinx` by default adds some template files which you are expected
to fill out located at:

- ``{root}/documentation/developer_documentation.rst``
- ``{root}/documentation/user_documentation.rst``

.. important::

    The next step, :ref:`rez_sphinx build run`, checks those default files for
    edits and fails + stops early if they're still default. So let's add some
    text to them.


Run this in your terminal to quickly append some edits to those files:

.. code-block:: sh

    echo "Some documentation for users here" >> ./documentation/user_documentation.rst
    echo "Some technical documentation" >> ./documentation/developer_documentation.rst


.. note::

    If this check is doing more harm than good, it can be disabled using
    :ref:`rez_sphinx.init_options.check_default_files`.


********************
rez_sphinx build run
********************

Your documentation is initialized and has some hand-written edits. You're ready
to build!

.. code-block:: sh

    rez-test your_package_name_here build_documentation

Congratulations, your documentation is now waiting for you in
``{root}/build/documentation/index.html``.

If all you want to do is get some documentation quickly up and running and
aren't too particular about the details, here's where the tutorial ends.  But
if you want to learn more about :ref:`rez_sphinx` and how it works, see the
sections below.
