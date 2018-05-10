# -*- coding: utf-8 -*-
class HattoriException(Exception):
    """
    An exception class for Hattori errors
    """
    def __init__(self, msg, original_exception=''):
        super().__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
