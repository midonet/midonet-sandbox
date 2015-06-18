# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import ConfigParser
import logging

from os.path import isfile


log = logging.getLogger('midonet-sandbox.configuration')

DEFAULT_SETTINGS = dict(
    extra_components=None
)


class Config(object):
    """
    Read and parse the configuration file. The configuration file format is:
    ---------------
    [sandbox]
    extra_components = None
    -----------------
    """

    DEFAULT_CONFIGURATION_FILE = '~/.midonet-sandboxrc'

    def __init__(self, config_file=DEFAULT_CONFIGURATION_FILE):

        log.info('Trying configuration file: {}'.format(config_file))
        if isfile(config_file):
            self._config = ConfigParser.RawConfigParser()
            self._config.read(config_file)
        else:
            self._config = DEFAULT_SETTINGS
            log.info(
                'Cannot read configuration {}. Using default settings'.format(
                    config_file))

        log.debug('Settings: {}'.format(self._config) )

    def get_default_value(self, param):
        # Using DEFAULT_SETTINGS
        if param in self._config:
            return self._config.get(param)

        return self._config.get('sandbox', param)