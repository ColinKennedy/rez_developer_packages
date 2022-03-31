from __future__ import print_function

from rez import release_hook


class PublishDocumentation(release_hook.ReleaseHook):
    @classmethod
    def name(cls):
        return "publish_documentation"

    def pre_release(self, user, install_path, variants=None, **kwargs):
        # TODO : Make this real
        raise ValueError('PRE RELEASING')
        print('PRE RELEASE')

    def post_release(self, user, install_path, variants, **kwargs):
        # TODO : Make this real
        print('POST RELEASE')


def register_plugin():
    return PublishDocumentation
