name = "contains_ephemeral"

version = "1.0.0"

requires = [
    # This ephemeral syntax is a "feature ephemeral", a Rez functionality that
    # doesn't exist just yet.  However even without it existing, it's still an
    # ephemeral so it's "valid" from the POV of writing unittests.
    #
    # Reference:
    #     https://github.com/nerdvegas/rez/issues/673
    #     REP-002.008: Package features [hard] [requires: 002.007]
    #
    ".contains_ephemeral.feature-1",
]
