# -*- coding: utf-8 -*-

name = 'second_complex_package'

version = '1.0.0'

requires = [
    'nested_dependency-1',
    'package_plus_pure_dependency-1',
    'pure_dependency-1'
]

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/installed_packages'
    config.packages_path = ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/installed_packages']
    config._CURRENT_DIRECTORY = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/source_packages'
    config.parent = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/suggestion_test_nested/installed_packages'

timestamp = 1647716321

format_version = 2
