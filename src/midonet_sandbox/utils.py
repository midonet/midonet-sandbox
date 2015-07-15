# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
from logging import StreamHandler
from logging.handlers import WatchedFileHandler

logger = logging.getLogger('midonet-sandbox')


def configure_logging(loglevel, logfile=None):
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
        logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s',
                          '%m-%d %H:%M:%S'))
    logger.addHandler(handler)


def exception_safe(exception, return_value):
    """
    Catch the exception, log it and return a value
    """

    def decorator(func):
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except exception, e:
                logger.error('A {} occurred: {}'.format(exception, e))
                return return_value

        return wrapper

    return decorator
