#################################################
Linking rez_sphinx With Other Documentation Tools
#################################################

Imagine you have 2 packages

- Your package
- Another package

And you want to link that "Another package" to Your package. "Another package"
is built with `Sphinx`_, but not :ref:`rez_sphinx`. Can you still link the two?

Yes. But it requires a small tweak to "Another package". You need to add a
"rez_sphinx objects.inv" key to its `package help`_ attribute:

.. code-block:: python

   name = "another_package"

   version = "1.2.3"

   # ... more stuff ...

   help = [
       # Add this key here
       ["rez_sphinx objects.inv", "http://www.company-docs.com/another_package/latest"],
   ]

Where ``"http://www.company-documentation.com/another_package/latest"``
is the top-level root of the built Sphinx documentation. And of course, it
doesn't have to be a URL. It could point to a directory on-disk instead.

As long as that's added, :ref:`rez_sphinx` mingles with existing documentation easily!
