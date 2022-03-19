# -*- coding: utf-8 -*-

name = 'another_nested'

version = '1.0.0'

requires = ['package_plus_pure_dependency-1']

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/installed_packages'
    config.packages_path = ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/installed_packages']
    config._CURRENT_DIRECTORY = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/source_packages'
    config.parent = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/installed_packages'

timestamp = 1647669123

format_version = 2
