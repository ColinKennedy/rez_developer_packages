import os


class EnvironmentMacro(object):
    def __init__(self, environment_variable, path):
        super(EnvironmentMacro, self).__init__()

        self._environment_variable = environment_variable
        self._path = path

    def has_match(self, root):
        return os.path.isdir(os.path.join(root, self._path))

    def get_commands(self):
        return [
            'env.{self._environment_variable}.append("{{root}}{os.sep}{self._path}")'.format(
                self=self, os=os,
            )
        ]
