class YaError(Exception):
    """Base class for exceptions in this module."""
    pass


class YaTypeConvertError(YaError):

    def __init__(self, expr, msg):
        YaError.__init__(self)
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return repr(self.msg)



class YaEmptyRequestError(YaError):

    def __init__(self, msg):
        YaError.__init__(self)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
