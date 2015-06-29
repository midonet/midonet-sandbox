# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import subprocess
import tempfile

import os
from yaml import load, dump
from midonet_sandbox.configuration import Config
from midonet_sandbox.assets.assets import Assets


class DockerComposer(object):
    """
    Wrapper around the docker-composer CLI
    """

    def __init__(self):
        self._config = Config.instance_or_die()
        self._assets = Assets()
        # set the DOCKER_HOST env var to point docker specified in the config
        self._env = os.environ.copy()
        self._env['DOCKER_HOST'] = self._config.get_sandbox_value(
            'docker_socket')

    def up(self, yml_file, name, override=None):
        """
        Spawn a composer job to orchestrate containers
        :param yml_file: the composer YML file full path
        :param name: the sandbox name
        :param override: the override path
        :return: the process output
        """

        final_yml = self._apply_substitutions(yml_file)

        if override:
            final_yml = self._apply_override(yml_file, override)

        return subprocess.Popen(['docker-compose', '-f', final_yml, '-p', name,
                                 'up', '-d'], stderr=subprocess.STDOUT,
                                env=self._env)

    def stop(self, name):
        return subprocess.Popen(['docker-compose', '-p', name, 'stop'],
                                stderr=subprocess.STDOUT, env=self._env)


    def _apply_substitutions(self, yml_file):
        """
        Apply variables substitution in the yml file
        :param yml_file: the original yml file
        :return: the modified yml file
        """
        base_composer_path = self._assets.get_abs_base_components_path()
        temp_yml = tempfile.NamedTemporaryFile(suffix='.yml', delete=False)

        vars = {
            '$BASE': base_composer_path
        }

        with open(yml_file, 'rb') as _f_yml:
            content = _f_yml.read()

            for var, value in vars.items():
                content = content.replace(var, value)

        temp_yml.write(content)
        return temp_yml.name

    def _apply_override(self, yml_file, override):
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

                # replace the base file with the abs_path
                base_file = os.path.split(definition['extends']['file'])[-1]

                definition['extends']['file'] = \
                    os.path.join(self._assets.get_abs_base_components_path(),
                                 base_file)

        temp_yml = tempfile.NamedTemporaryFile(suffix='.yml', delete=False)

        dump(yml_content, temp_yml)
        return temp_yml.name

