# -*- coding: utf-8 -*-

name = 'no_documentation'

version = '1.0.0'

private_build_requires = ['python']

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/existing_documentation/installed_packages'
    config._CURRENT_DIRECTORY = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/existing_documentation/source_packages'
    config.parent = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/existing_documentation'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/existing_documentation/installed_packages'

timestamp = 1647744140

format_version = 2
