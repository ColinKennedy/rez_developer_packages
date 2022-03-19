# -*- coding: utf-8 -*-

name = 'pure_dependency'

version = '1.0.0'

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/unknown_folder_structure/installed_packages'
    config.packages_path = ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/unknown_folder_structure/installed_packages']
    config._CURRENT_DIRECTORY = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/unknown_folder_structure/source_packages/inner_folder'
    config.parent = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/unknown_folder_structure'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/tests/data/unknown_folder_structure/installed_packages'

timestamp = 1647668887

format_version = 2
