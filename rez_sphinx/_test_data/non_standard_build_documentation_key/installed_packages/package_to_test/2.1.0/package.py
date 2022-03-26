# -*- coding: utf-8 -*-

name = 'package_to_test'

version = '2.1.0'

requires = [
    'python',
    'some_package-1+'
]

def commands():
    import os
    
    env.PYTHONPATH.append(os.path.join(root, "python"))

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key/installed_packages'
    config.packages_path = \
        ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key/installed_packages',
         '/home/selecaoone/packages']
    config.current_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key/source_packages/package_to_test'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key'

timestamp = 1648267368

tests = \
    {'build_documentation': {'command': 'rez_sphinx build',
                             'requires': ['another_package-1+<2',
                                          'rez_sphinx-1.0+<2']}}

format_version = 2
