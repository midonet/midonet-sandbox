# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura
import logging
import subprocess
from collections import Counter

import os
from injector import inject, singleton
from requests.exceptions import ConnectionError
from yaml import load
from midonet_sandbox.configuration import Config
from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.exceptions import FlavourNotFound
from midonet_sandbox.logic.container import ContainerBuilder
from midonet_sandbox.utils import exception_safe
from midonet_sandbox.wrappers.docker_wrapper import Docker
from midonet_sandbox.wrappers.composer_wrapper import DockerComposer

log = logging.getLogger('midonet-sandbox.composer')


@singleton
class Composer(object):
    """
    """

    SANDBOX_PREFIX = 'mnsandbox'

    @inject(config=Config, docker=Docker, assets=Assets,
            composer=DockerComposer, container_builder=ContainerBuilder)
    def __init__(self, config, docker, assets, composer, container_builder):
        self._config = config
        self._assets = assets
        self._docker = docker
        self._composer = composer
        self._container_builder = container_builder

    @exception_safe(ConnectionError, False)
    def run(self, flavour, name, force=False, override=None, provision=None,
            no_recreate=False):
        """
        :param flavour: The flavour name
        :param name: The sandbox name
        :param force: Force restarting without asking
        :param override: An override path
        :param provision: A provisioning script path
        :param no_recreate: Do not recreate containers if they exist on restart
        :return: True if the sandbox has been started, False otherwise
        """
        message = 'Spawning {} sandbox'.format(flavour)
        if override:
            message += ' with override {}'.format(override)

        log.info(message)

        if flavour not in self._assets.list_flavours():
            log.error('Cannot find flavour {}. Aborted'.format(flavour))
            return

        flavour_file = self._assets.get_abs_flavour_path(flavour)
        override = os.path.abspath(override) if override else None

        restart = 'y'
        if not force:
            running_sandboxes = self.list_running_sandbox()
            if name in running_sandboxes:
                restart = raw_input(
                    "\nSandbox {} is already up. Restart? (Y/N): ".format(name))

        if force or restart.lower() == 'y':
            composer = \
                self._composer.up(flavour_file,
                                  '{}{}'.format(self.SANDBOX_PREFIX, name),
                                  override, no_recreate)
            composer.wait()

            if provision:
                provision = os.path.abspath(provision)
                if os.path.isfile(provision) and os.access(provision, os.X_OK):
                    log.info(
                        'Running provisioning script: {}'.format(provision))
                    provisioning_env = {
                        "SANDBOX_NAME": name
                    }
                    p = subprocess.Popen(
                        provision, stderr=subprocess.STDOUT,
                        env=dict(os.environ, **provisioning_env))
                    p.wait()
                else:
                    log.error(
                        'File {} does not exist or it\'s not executable'.format(
                            provision
                        ))
                    return False

        return True

    @staticmethod
    def __get_sandbox_name(container_name):
        return container_name.split('_')[0].replace(Composer.SANDBOX_PREFIX,
                                                    '').replace('/', '')

    @exception_safe(ConnectionError, [])
    def list_running_sandbox(self):
        """
        List all the running sandbox
        :return: The list of all the running sandbox
        """
        sandoxes = set()
        containers = self._docker.list_containers(self.SANDBOX_PREFIX)
        for container_ref in containers:
            container = self._container_builder.for_container_ref(container_ref)
            sandoxes.add(self.__get_sandbox_name(container.name))

        return sandoxes

    @exception_safe(ConnectionError, None)
    def stop(self, sandboxes, remove=False):
        """
        Stop the running sandbox
        """
        return self._map_stop_or_kill('stop', sandboxes, remove)

    @exception_safe(ConnectionError, None)
    def kill(self, sandboxes, remove=False):
        """
        Kill the running sandbox
        """
        return self._map_stop_or_kill('kill', sandboxes, remove)

    @exception_safe(ConnectionError, [])
    def get_sandbox_detail(self, sandbox):
        """

        :param sandbox:
        :return:
        """
        containers = list()
        for container_ref in self._docker.list_containers(
                '{}{}_'.format(self.SANDBOX_PREFIX, sandbox)):

            container = self._container_builder.for_container_ref(container_ref)
            ip = container.ip
            name = container.name
            image = container.image
            ports = container.ports(pretty=True)

            containers.append([sandbox, name, image, ports, ip])

        return containers

    @exception_safe(FlavourNotFound, dict())
    def get_components_by_flavour(self, flavour):
        """
        """
        flavour_path = self._assets.get_abs_flavour_path(flavour)
        components = list()
        with open(flavour_path, 'rb') as _f_yml:
            yml_content = load(_f_yml)
            for component, definition in yml_content.items():
                if 'image' in [c.lower() for c in definition]:
                    components.append(definition['image'])
                else:

                    extended = definition['extends']['file']
                    for var, value in self._composer.VARS.items():
                        extended = extended.replace(var, value)
                    service = definition['extends']['service']
                    image = self._get_base_component_image(extended, service)
                    if ':' not in image:
                        image = '{}:master'.format(image)
                    if image:
                        components.append(image)

        return Counter(components)

    def _get_base_component_image(self, yml, service):
        """
        """
        # If it's a relative path, search for it in the extra flavours directory
        if not os.path.isabs(yml):
            extra_flavours = self._config.get_sandbox_value('extra_flavours')
            if extra_flavours:
                yml = os.path.join(extra_flavours, yml)

        with open(yml, 'rb') as _f_yml:
            component_content = load(_f_yml)
            for component, definition in component_content.items():
                if component == service:
                    return definition['image']

        return None

    def _map_stop_or_kill(self, op, sandboxes, remove=False):
        """
        Stop/Kill the running sandbox
        """
        running_sandboxes = self.list_running_sandbox()

        for sandbox in sandboxes:
            if sandbox not in running_sandboxes:
                log.info('Sandbox {} not running. Skipping'.format(sandbox))
                continue

            containers = self._docker.list_containers(
                '{}{}_'.format(self.SANDBOX_PREFIX, sandbox))

            for container_ref in containers:
                container = self._container_builder.for_container_ref(
                    container_ref)
                service_name = container.service_name
                log.info('Sandbox {} - {}ing container {}'.format(sandbox,
                                                                  op,
                                                                  service_name))

                docker_op = op + '_container'
                getattr(self._docker, docker_op)(container_ref)
                if remove:
                    log.info('Sandbox {} - Removing '
                             'container {}'.format(sandbox, service_name))

                    self._docker.remove_container(container_ref)
        return True
