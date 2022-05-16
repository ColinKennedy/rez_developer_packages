class Base(Exception):
    code = 1


class ContextNotFound(Base):
    code = 10


class InvalidContext(Base):
    code = 20
