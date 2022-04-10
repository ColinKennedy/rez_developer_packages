###########################
Batch-Publish Documentation
###########################

If you want to add documentation in-batch, the steps are very similar to
:doc:`getting_started`, with some adjustments.

.. important::

   If you want auto-linking, auto-publishing, and the like to work, you must
   opt-in to those features before following this tutorial.

   Follow the steps in :doc:`rez_sphinx_as_a_release_hook` first before continuing.


- cd to the root of some git repository containing **source** Rez packages
- Run this in the terminal:

.. code-block:: sh

    export REZ_SPHINX_INIT_OPTIONS_CHECK_DEFAULT_FILES=0

    directories=`rez_sphinx suggest build-order . --search-mode source --display-as directories`
    root=$PWD

    for directory in $directories
    do
        cd $directory

        package_name=`get_package_name`
        package_version=`get_package_version`

        rez-build --clean --install
        rez-env $package_name==$package_version rez_sphinx -- rez_sphinx init
        rez-release -m "Added rez_sphinx documentation"
    done

    cd $root
    git add --all
    git commit -m "Added rez_sphinx documentation everywhere"

    unset REZ_SPHINX_INIT_OPTIONS_CHECK_DEFAULT_FILES
