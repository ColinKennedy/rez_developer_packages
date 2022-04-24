##############
Authenticating
##############

This page explains the different ways you can connect to remote services like
GitHub. To do this, must must provide :ref:`rez_docbot` with log-in
credentials (username and password, access token, etc).

A typical authentication configuration may look like this `rezconfig.py`_:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher information ...
                    "authentication": {
                        "token": "kjhaweliufhawe_some_access_token_asiudfhasdf",
                        "user": "MyUser",
                    },
                    "type": "github",
                    # ... More publisher information ...
                },
            ],
        }

It's important to remember these following types:

- You do not need to directly write authentication details directly in `rezconfig.py`_
    - See :ref:`authentication indirection`


In general, :ref:`rez_docbot` doesn't put any hard requirements for how publishers
authenticate. As long as the publisher provides a :meth:`.Publisher.authenticate` method,

the methodology for authenticating to a remote service is completely up to th


.. _authentication indirection:

Authentication Indirection
==========================

Putting raw user / token credenticals in a `rezconfig.py`_ that someone can
conceivably view by calling ``rez-config optionvars`` is not good `OPSEC`_. To
make it a bit harder for users to see sensitive log-in information, you can
tell publishers such as the :ref:`github publisher type` to read authentication
details from a file, like so:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher information ...
                    "authentication": {
                        "payload": "~/.github_authentication_test.json",
                        "type": "from_json_path",
                    },
                    "type": "github",
                    # ... More publisher information ...
                },
            ],
        }


That file, ``~/.github_authentication_test.json``, may look like this:

.. code-block:: json

    {
        "token": "kjhaweliufhawe_some_access_token_asiudfhasdf",
        "user": "MyUser",
    }

If that file is only available from your local computer or otherwise difficult to access,
that can provide some additional security.

That said though, if we're talking about GitHub, access tokens can be given
limited permission sets so even if a bad actor got those log-in details, they
wouldn't be able to do much with it as long as your token is set correctly.

To see rez_docbot's recommended GitHub permissions settings, see
:doc:`github_access_tokens`.
