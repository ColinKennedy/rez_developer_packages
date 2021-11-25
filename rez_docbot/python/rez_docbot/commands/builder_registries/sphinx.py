from . import base


class Plugin(base.Plugin):
    @staticmethod
    def get_name():
        return "sphinx"
