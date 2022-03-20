# -*- coding: utf-8 -*-

name = 'pure_dependency'

version = '1.0.0'

with scope('config') as config:
    config.local_packages_path = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/resolve_requires/installed_packages'
    config.packages_path = ['/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/resolve_requires/installed_packages']
    config._CURRENT_DIRECTORY = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/resolve_requires/source_packages'
    config.parent = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/resolve_requires'
    config.root = '/home/selecaoone/env/config/rez_developer_packages/rez_sphinx/_test_data/resolve_requires/installed_packages'

timestamp = 1647750082

format_version = 2
