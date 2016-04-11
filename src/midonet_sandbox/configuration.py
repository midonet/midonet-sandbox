# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import ConfigParser
import logging
from StringIO import StringIO

import os
from os.path import isfile

log = logging.getLogger('midonet-sandbox.configuration')

DEFAULT_SETTINGS = {
    'extra_flavours': None,
    'extra_components': None,
    'docker_socket': 'unix://var/run/docker.sock',
    'docker_remove_intermediate': False,
    'docker_registry': None,
    'docker_insecure_registry': False,
    'docker_http_timeout': '300'
}


class Config(object):
    """
    Read and parse the configuration file. The configuration file format is:
    ---------------
    [sandbox]
    extra_flavours = <path_to_extra_flavours_directory>
    extra_components = <path_to_extra_flavours_directory>
    docker_socket = unix://var/run/docker.sock
    docker_remove_intermediate = True
    docker_registry = None
    docker_insecure_registry = False
    -----------------
    """

    def __init__(self, config_file):
        self._config = ConfigParser.SafeConfigParser(defaults=DEFAULT_SETTINGS)
        config_file = os.path.expanduser(config_file)

        if isfile(config_file):
            log.info('Loading configuration file: {}'.format(config_file))
            self._config.read(config_file)
        else:
            self._config.add_section('sandbox')
            if not isfile(config_file):
                log.info('Cannot read {}'.format(config_file))
            log.info('Using default settings')

        log.debug('Settings: \n{}'.format(self.dump_config(self._config)))

    def get_sandbox_value(self, param):
        return self._config.get('sandbox', param)

    @staticmethod
    def dump_config(config):
        dump = StringIO()
        config.write(dump)
        return dump.getvalue()
