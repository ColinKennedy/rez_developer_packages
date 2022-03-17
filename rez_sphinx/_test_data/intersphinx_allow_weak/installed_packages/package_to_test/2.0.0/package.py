# -*- coding: utf-8 -*-

name = 'package_to_test'

version = '2.0.0'

requires = [
    'dependency_which_specifies_the_weak_requires-1+',
    '~weak_package-1+<2'
]

def commands():
    import os
    
    env.PYTHONPATH.append(os.path.join(root, "python"))

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak/installed_packages'
    config.packages_path = ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak/installed_packages']
    config.current_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak/source_packages/package_to_test'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak'

timestamp = 1647396531

format_version = 2
