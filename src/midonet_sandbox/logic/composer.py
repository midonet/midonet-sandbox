# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura



import logging
from collections import Counter
from midonet_sandbox.exceptions import FlavourNotFound

import os
from requests.exceptions import ConnectionError
from yaml import load
from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.configuration import Config
from midonet_sandbox.utils import exception_safe
from midonet_sandbox.wrappers.composer_wrapper import DockerComposer
from midonet_sandbox.wrappers.docker_wrapper import Docker

log = logging.getLogger('midonet-sandbox.composer')


class Composer(object):
    """
    """

    SANDBOX_PREFIX = 'mnsandbox'

    def __init__(self):
        configuration = Config.instance_or_die()
        self._assets = Assets()
        self._docker = Docker(configuration.get_sandbox_value('docker_socket'))
        self._composer = DockerComposer()

    @exception_safe(ConnectionError, None)
    def run(self, flavour, name, force, override):

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
                                  override)
            composer.wait()
            return True

        return False

    @staticmethod
    def __get_sandbox_name(container_name):
        return container_name.split('_')[0].replace(Composer.SANDBOX_PREFIX,
                                                    '').replace('/', '')

    @staticmethod
    def __get_service_name(container_name):
        return '_'.join(container_name.split('_')[1:])

    @exception_safe(ConnectionError, [])
    def list_running_sandbox(self):
        """
        List all the running sandbox
        :return: The list of all the running sandbox
        """

        sandoxes = set()
        containers = self._docker.list_containers(self.SANDBOX_PREFIX)
        for container in containers:
            sandoxes.add(self.__get_sandbox_name(
                self.__get_container_name(container['Names'])))

        return sandoxes

    @exception_safe(ConnectionError, None)
    def stop(self, sandboxes, remove=False):
        """
        Stop the running sandbox

        :param sandbox:
        :return:
        """

        running_sandboxes = self.list_running_sandbox()

        for sandbox in sandboxes:
            if sandbox not in running_sandboxes:
                log.info('Sandbox {} not running. Skipping'.format(sandbox))
                continue

            containers = self._docker.list_containers(
                '{}{}_'.format(self.SANDBOX_PREFIX, sandbox))

            for container in containers:
                service_name = self.__get_service_name(
                    self.__get_container_name(container['Names']))
                log.info('Sandbox {} - Stopping container {}'.format(sandbox,
                                                                     service_name))
                self._docker.stop_container(container)
                if remove:
                    log.info('Sandbox {} - Removing '
                             'container {}'.format(sandbox, service_name))

                    self._docker.remove_container(container)

    @staticmethod
    def __format_ports(ports):
        ports_list = list()
        for port in ports:
            if 'PublicPort' in port:
                ports_list.append(
                    '{}/{}->{}:{}'.format(port['Type'], port['PrivatePort'],
                                          port['IP'], port['PublicPort']))
            else:
                ports_list.append(
                    '{}/{}'.format(port['Type'], port['PrivatePort']))

        return ','.join(sorted(ports_list))

    @staticmethod
    def __get_container_name(names):
        for name in names:
            name = name[1:]
            if '/' not in name:
                return name

    @exception_safe(ConnectionError, [])
    def get_sandbox_detail(self, sandbox):
        """

        :param sandbox:
        :return:
        """
        containers = list()
        for container in self._docker.list_containers(
                '{}{}_'.format(self.SANDBOX_PREFIX, sandbox)):

            ip = self._docker.container_ip(container)
            name = self.__get_container_name(container['Names'])
            image = container['Image']
            ports = self.__format_ports(container['Ports'])

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

                    file = definition['extends']['file']
                    for var, value in self._composer.VARS.items():
                        file = file.replace(var, value)
                    service = definition['extends']['service']
                    image = self._get_base_component_image(file, service)
                    if image:
                        components.append(image)

        return Counter(components)

    @staticmethod
    def _get_base_component_image(file, service):
        """
        """
        with open(file, 'rb') as _f_yml:
            component_content = load(_f_yml)
            for component, definition in component_content.items():
                if component == service:
                    return definition['image']

        return None
