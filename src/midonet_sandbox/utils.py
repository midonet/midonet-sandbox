# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
from logging import StreamHandler
from logging.handlers import WatchedFileHandler

logger = logging.getLogger('midonet-sandbox')

# Code adapted from:
# http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self, *args, **kwargs):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated(*args, **kwargs)
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')


def configure_logging(loglevel, logfile=None):
    class LoggerWriter:
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level

        def write(self, message):
            for line in message.rstrip().splitlines():
                self.logger.log(self.level, line.rstrip())

    loglevel = loglevel.upper()
    loglevels = ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    if loglevel not in loglevels:
        raise Exception('Loglevel must be one of {}'.format(loglevels))

    logger.setLevel(getattr(logging, loglevel))
    if logfile:
        handler = WatchedFileHandler(logfile)
    else:
        handler = StreamHandler()
    handler.setFormatter(
        logging.Formatter('[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d}'
                          ' %(levelname)s - %(message)s', '%m-%d %H:%M:%S'))
    logger.addHandler(handler)
