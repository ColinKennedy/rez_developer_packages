from . import base


class Plugin(base.BuilderPlugin):
    @staticmethod
    def get_name():
        return "sphinx"
