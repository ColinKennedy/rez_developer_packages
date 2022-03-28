class Repository(object):
    def __init__(self, repository):
        super(Repository, self).__init__()

        self._repository = repository

    def clone_to(self, directory):
        raise NotImplementedError(directory)
