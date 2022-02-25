import os

from . import rpm_macro


# TODO : Check if this environment variable works
_BIN = rpm_macro.EnvironmentMacro("PATH", os.path.join("usr", "bin"))
# TODO : Maybe in clude C_INCLUDE_PATH?
_INCLUDE = rpm_macro.EnvironmentMacro("CPP_INCLUDE_PATH", os.path.join("usr", "include"))
_LIBEXEC = rpm_macro.EnvironmentMacro("PATH", os.path.join("usr", "libexec"))
_SBIN = rpm_macro.EnvironmentMacro("PATH", os.path.join("usr", "sbin"))
_USR_LIB64_LD = rpm_macro.EnvironmentMacro("LD_LIBRARY_PATH", "lib64")
_USR_LIB64_LIBRARY = rpm_macro.EnvironmentMacro("LIBRARY_PATH", "lib64")
_USR_LIB_LD = rpm_macro.EnvironmentMacro("LD_LIBRARY_PATH", os.path.join("usr", "lib"))
_USR_LIB_LIBRARY = rpm_macro.EnvironmentMacro("LIBRARY_PATH", os.path.join("usr", "lib"))
_USR_LIB64_LD = rpm_macro.EnvironmentMacro("LD_LIBRARY_PATH", os.path.join("usr", "lib64"))
_USR_LIB64_LIBRARY = rpm_macro.EnvironmentMacro("LIBRARY_PATH", os.path.join("usr","lib64"))
_LIB_LD = rpm_macro.EnvironmentMacro("LD_LIBRARY_PATH", "lib")
_LIB_LIBRARY = rpm_macro.EnvironmentMacro("LIBRARY_PATH", "lib")
_LIB64_LD = rpm_macro.EnvironmentMacro("LD_LIBRARY_PATH", "lib64")
_LIB64_LIBRARY = rpm_macro.EnvironmentMacro("LIBRARY_PATH", "lib64")
_SHARE_MAN = rpm_macro.EnvironmentMacro("MANPATH", os.path.join("usr", "share", "man"))

# TODO : Include /usr/share later

_MACROS = [
    _BIN,
    _INCLUDE,
    _LIB64_LD,
    _LIB64_LIBRARY,
    _LIBEXEC,
    _LIB_LD,
    _LIB_LIBRARY,
    _SBIN,
    _SHARE_MAN,
    _USR_LIB64_LD,
    _USR_LIB64_LIBRARY,
    _USR_LIB_LD,
    _USR_LIB_LIBRARY,
]


def get_package_commands(root):
    # Reference: https://docs.fedoraproject.org/en-US/packaging-guidelines/RPMMacros/#macros_installation
    if not os.path.isdir(root):
        raise ValueError('Path "{root}" is not a directory.'.format(root=root))

    output = set()

    for macro in _MACROS:
        if macro.has_match(root):
            output.update(macro.get_commands())

    return output
