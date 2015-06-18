# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import sys
import logging

from logging import StreamHandler
from logging.handlers import WatchedFileHandler

logger = logging.getLogger('midonet-sandbox')


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

    sys.stdout = LoggerWriter(logger, getattr(logging, loglevel))
    sys.stderr = LoggerWriter(logger, logging.ERROR)