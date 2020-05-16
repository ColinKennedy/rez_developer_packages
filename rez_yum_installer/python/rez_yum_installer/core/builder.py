#!/usr/bin/env python
# -*- coding: utf-8 -*-



#     spec = spec_.Spec.from_file("/tmp/rmp_test/xdotool.spec")
#
#     import os
#     import sys
#     sys.path.append(os.path.join(os.path.expanduser('~'), 'env/config/rez_packages/utils/python'))
#     from inspection import dirgrep
#     dirgrep(spec, '', sort=True)
#     text = \
# """
# %install
# rm -rf $RPM_BUILD_ROOT
# make PREFIX=$RPM_BUILD_ROOT/%{_prefix} INSTALLMAN=$RPM_BUILD_ROOT%{_mandir} INSTALLLIB=$RPM_BUILD_ROOT%{_libdir} install
# """
#     print(spec_.replace_macros(text))
#     print(spec.sources)
#     print(spec.release)
#     print(spec.obsoletes)
#     print(spec.license)
#     print(spec.group)
#     print(spec.define)
#     print(spec.buildroot)
#     print(spec.buildarch)
#     print(spec.packages)
#     print(spec.sources)
#     print(spec.sources_dict)
#
#     # package = spec.packages[0]
#     # import os
#     # import sys
#     # sys.path.append(os.path.join(os.path.expanduser('~'), 'env/config/rez_packages/utils/python'))
#     # from inspection import dirgrep
#     # dirgrep(package, '', sort=True)
#     # print(package.build_requires)
#     # print(package.requires)
#     # print(package.provides)
#     # print(package.name)
#     # print(package.obsoletes)
#     # print(package.conflicts)
#     # print(package.is_subpackage)
#
