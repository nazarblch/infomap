class Error(Exception):
    """Base class for exceptions in this module."""

    def __str__(self):
        return repr(self.msg)

class YMLError(Error):
    """Exception raised for errors occurred during XML parsing."""

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
        print "YMLError \n" + "msg: " + str(msg) + "\n" + "expr: " + str(expr) + "\n"

class OutOfRangeError(Error):
    """Exception raised for out of range value errors."""

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
