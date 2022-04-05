- Do CI changes so far


Features
- bisect run to work
- Standard git bisect interactivity

- The report should say
 - The first index that has the problem (+ include the request that failed)
 - Diff that index with the previous one, show its result
 - If --partial is included, **guess** what the issue could be, based on the diff


Test Cases
- Multi package issues
 - 2 or more packages at once have some incompatible issue

- Handle errors due to added or removed **ephemerals**

Documentation
:ref:`rez_bisect`
:ref:`.rxt`
:ref:`request`."""
:ref:`--partial`
- :ref:`rez_bisect run`

- Add tags to docstrings as needed (add them where they don't exist)
- :ref:`contexts`
