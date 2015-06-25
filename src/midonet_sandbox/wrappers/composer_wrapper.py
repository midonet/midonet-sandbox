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
        # set the DOCKER_HOST env var to point docker specified in the config
        self._env = os.environ.copy()
        self._env['DOCKER_HOST'] = self._config.get_default_value(
            'docker_socket')


    def up(self, yml_file, name):
        """
        Spawn a composer job to orchestrate containers
        :param yml_file: the composer YML file full path
        :param yml_file: the sandbox name
        :return: the process output
        """

        return subprocess.Popen(['docker-compose', '-f', yml_file, '-p', name,
                                 'up', '-d'], stderr=subprocess.STDOUT,
                                env=self._env)

    def stop(self, name):
        return subprocess.Popen(['docker-compose', '-p', name, 'stop'],
                         stderr=subprocess.STDOUT, env=self._env)