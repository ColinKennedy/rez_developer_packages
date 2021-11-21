class BaseException(Exception):
    code = 1


class IsNotBad(BaseException):
    code = 2


class IsNotGood(BaseException):
    code = 3
