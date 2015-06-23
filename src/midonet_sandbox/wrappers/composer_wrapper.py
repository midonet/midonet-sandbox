# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import subprocess

import os
from midonet_sandbox.configuration import Config


class DockerComposer(object):
    """
    Wrapper around the docker-composer CLI
    """

    def __init__(self):
        self._config = Config.instance_or_die()


    def up(self, yml_file):
        """
        Spawn a composer job to orchestrate containers
        :param yml_file: the composer YML file full path
        :return: the process output
        """
        # set the DOCKER_HOST env var to point docker specified in the config
        env = os.environ.copy()
        env['DOCKER_HOST'] = self._config.get_default_value('docker_socket')

        return subprocess.Popen(['docker-compose', '-f', yml_file, 'up'],
                                stderr=subprocess.STDOUT, env=env)
