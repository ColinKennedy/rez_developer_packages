# -*- coding: utf-8 -*-

name = 'dependency_which_specifies_the_weak_requires'

version = '7.0.0'

requires = ['weak_package-1+']

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak/installed_packages'
    config.packages_path = ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak/installed_packages']
    config.current_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak/source_packages/dependency_which_specifies_the_weak_requires'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/intersphinx_allow_weak'

timestamp = 1647396460

format_version = 2
