# -*- coding: utf-8 -*-

name = 'some_package'

version = '1.0.0'

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/conflicting_names/installed_packages'
    config._CURRENT_DIRECTORY = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/conflicting_names/source_1'
    config.parent = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/conflicting_names'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/conflicting_names/installed_packages'

timestamp = 1647745879

format_version = 2
