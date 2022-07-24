# TODO
## Generic
- Allow "nudging" - If the partial bisect fails midway, it should "shift" the
  packages "left / right" to see if it can create a passing resolve
- Make sure custom --packages-path is supported, all the way down even during diffing
- Make sure that bisect_2d pays attention to allowed requests
	- e.g. picking a midpoint package that isn't allowed by the original request should not be possible
	- e.g. picking a midpoint that is disallowed by the requirements of resolved packages should not be possible


## CLI Functionality
- When a generic report is generated, Offer for users to re-run with --partial
  to get more refined results
- Allow the bisect to be interactive (right now, you have to provide a script)

## Cases
- Multi package issues
 - 2 or more packages at once have some incompatible issue
- Handle errors due to added or removed **ephemerals**

- Ephemeral - newer range
- Ephemeral - older range
- A package with an ephemeral variant that a request picks up

- To make bisecting faster, I should try removing package versions from the
  diff which do not satisfy the package requests from the bad context. After
  all, if the package version is not allowed in the bad context's request,
  there's no possibility of them actually being in the resolve so that means
  the excluded versions are not a factor in what made the bad context, bad!

- The report should say
 - The first index that has the problem (+ include the request that failed)
 - Diff that index with the previous one, show its result
 - If --partial is included, **guess** what the issue could be, based on the diff

Documentation
:ref:`--packages-path`
:ref:`--partial`
:ref:`.rxt`
:ref:`automated Rez bisect`
:ref:`contexts`
:ref:`contexts`
:ref:`request`
:ref:`package family`
:ref:`--partial`
:ref:`installed`

- :ref:`requests`
:ref:`request`."""
:ref:`rez_bisect cli`."""
:ref:`rez_bisect run`
:ref:`rez_bisect`
