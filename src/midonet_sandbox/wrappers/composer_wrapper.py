# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
import subprocess
import tempfile

import os
from yaml import load, dump
from midonet_sandbox.configuration import Config
from midonet_sandbox.assets.assets import Assets
from injector import inject, singleton

log = logging.getLogger('midonet-sandbox.dockercomposer')


@singleton
class DockerComposer(object):
    """
    Wrapper around the docker-composer CLI
    """

    VARS = {
        '$BASE': Assets.get_abs_base_components_path()
    }

    @inject(config=Config, assets=Assets)
    def __init__(self, config, assets):
        self._config = config
        self._assets = assets

        # set the DOCKER_HOST env var to point docker specified in the config
        self._env = os.environ.copy()
        self._env['DOCKER_HOST'] = \
            self._config.get_sandbox_value('docker_socket')

    def up(self, yml_file, name, override=None):
        """
        Spawn a composer job to orchestrate containers
        :param yml_file: the composer YML file full path
        :param name: the sandbox name
        :param override: the override path
        :return: the process output
        """

        temp_yml = self._apply_substitutions(yml_file)

        if override:
            temp_yml = self._apply_override(temp_yml, override)

        temp_yml = self._replace_relative_paths(yml_file, temp_yml)

        command = ['docker-compose', '-f', temp_yml, '-p', name, 'up', '-d']
        log.debug('Running external process: {}'.format(' '.join(command)))

        return subprocess.Popen(command, stderr=subprocess.STDOUT,
                                env=self._env)

    def stop(self, name):
        command = ['docker-compose', '-p', name, 'stop']
        log.debug('Running external process: {}'.format(' '.join(command)))

        return subprocess.Popen(command,
                                stderr=subprocess.STDOUT, env=self._env)

    def _apply_substitutions(self, yml_file):
        """
        Apply variables substitution in the yml file
        :param yml_file: the original yml file
        :return: the modified yml file
        """
        temp_yml = tempfile.NamedTemporaryFile(suffix='.yml', delete=False)

        with open(yml_file, 'rb') as _f_yml:
            content = _f_yml.read()

            for var, value in self.VARS.items():
                content = content.replace(var, value)

        temp_yml.write(content)
        return temp_yml.name

    @staticmethod
    def _apply_override(yml_file, override):
        """
        Apply the override patch to the yml file and return a new yml file
        :param yml_file: the original flavour description
        :param override: the override path
        :return: the new overridden yml file
        """
        components = os.listdir(override)

        with open(yml_file, 'rb') as _f_yml:
            yml_content = load(_f_yml)
            for component, definition in yml_content.items():
                service = None
                if 'extends' in definition:
                    service = definition['extends']['service']
                if service in components:

                    override_path = os.path.join(override, service)
                    if not override_path.endswith('/'):
                        override_path = '{}/'.format(override_path)

                    volume = '{}:/override:ro'.format(override_path)

                    if 'volumes' in definition:
                        definition['volumes'].append(volume)
                    else:
                        definition['volumes'] = [volume]

                    definition['command'] = '/override/override.sh'

        temp_yml = tempfile.NamedTemporaryFile(suffix='.yml', delete=False)

        dump(yml_content, temp_yml)
        return temp_yml.name

    @staticmethod
    def _replace_relative_paths(yml_file, tmp_yml):
        """
        Replace the relative paths in the temp file to abs path that refers
        to the original yml base path
        """
        local_path = os.path.split(yml_file)[0]

        with open(tmp_yml, 'rb') as _f_yml:
            yml_content = load(_f_yml)
            for component, definition in yml_content.items():
                if 'extends' in definition:
                    extended = definition['extends']['file']
                    if not os.path.isabs(extended):
                        abs_path = os.path.join(local_path, extended)
                        log.debug('Replacing relative path {} with {}'.format(
                            extended, abs_path
                        ))
                        definition['extends']['file'] = abs_path

        temp_yml = tempfile.NamedTemporaryFile(suffix='.yml', delete=False)
        dump(yml_content, temp_yml)
        return temp_yml.name
