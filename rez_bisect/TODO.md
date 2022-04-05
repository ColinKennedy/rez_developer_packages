Features
- Offer for users to re-run with --partial once the case has been narrowed down
- bisect run to work
- Standard git bisect interactivity

- Allow the user to pass a .rxt file, for a raw set of package requests
 - If given something that looks like a .rxt file (but isn't), fail with a good message


- Make sure failed contexts are not allowed to continue
 - Add an option, when dealing with multiple requests, to remove failed
   contexts (but warn the user)


Test Cases
- included package family is bad
- included package version is bad
- removed package family is bad
- removed package version is bad

- Changing variant within the same package causes some issue to occur
 - e.g. foo variant 0 == good, foo variant 1 has some kind of breakage

- If one of the resolve request steps has a conflict, skip it and go compare against the next one
 - Unless it can't
- TODO : Filter out duplicate requests, if the user provides any
 - If the start and end are the same request, fail with a unique message


Documentation
- :ref:`rez_bisect run`
