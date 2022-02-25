# TODO : Make this whole module better later
def _get_any(version):
    return ""


def _get_exact_match(version):
    return "=={version}".format(version=version)


def _get_less_than_or_equal(version):
    return "<={version}".format(version=version)


def _get_greater_than_or_equal(version):
    return "-{version}+".format(version=version)


_FLAG_MODES = {
    12: _get_greater_than_or_equal,
    16384: _get_any,
    16777226: _get_less_than_or_equal,
    8: _get_exact_match,
}


def get_require_text(version, require_flag):
    # TODO: Make sure epochs are handled properly, too
    #
    # Reference: https://rpm-software-management.github.io/rpm/manual/dependencies.html
    # Reference: 9:5.00502-3. I'll need to especially careful about handling version ranges when dealing with epochs
    #
    try:
        caller = _FLAG_MODES[require_flag]
    except KeyError:
        raise ValueError(
            'Flag "{require_flag}" is invalid. Options were, "{options}".'.format(
                require_flag=require_flag,
                options=sorted(_FLAG_MODES.keys())
            )
        )

    if version and caller == _get_any:
        # Note: This isn't actually an error. But I don't know how to
        # handle this case yet so I'd like to make sure it doesn't ever
        # happen accidentally.
        #
        raise NotImplementedError(
            'Got Flag "{require_flag}" and version "{version}".'.format(
                require_flag=require_flag, version=version
            )
        )

    return caller(version)
