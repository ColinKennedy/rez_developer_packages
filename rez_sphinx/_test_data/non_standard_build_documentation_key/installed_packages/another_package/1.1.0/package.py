# -*- coding: utf-8 -*-

name = 'another_package'

version = '1.1.0'

requires = ['python']

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key/installed_packages'
    config.current_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key/source_packages/another_package'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/non_standard_build_documentation_key'

timestamp = 1648267363

format_version = 2
