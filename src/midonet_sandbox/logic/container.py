# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from midonet_sandbox.wrappers.docker_wrapper import Docker

from midonet_sandbox.configuration import Config
from midonet_sandbox.exceptions import ContainerNotFound
from midonet_sandbox.utils import exception_safe

log = logging.getLogger('midonet-sandbox.container')


class Container(object):
    """
    Simple container operations
    """

    def __init__(self, container):
        self._docker = Docker(
            Config.instance_or_die().get_sandbox_value('docker_socket'))
        self._container = container

    @classmethod
    @exception_safe(ContainerNotFound, None)
    def for_name(cls, name):
        docker = Docker(
            Config.instance_or_die().get_sandbox_value('docker_socket'))

        container = docker.container_by_name(name)
        if not container:
            raise ContainerNotFound('Container {} not found'.format(name))

        return cls(container)

    def execute(self, command):
        self._docker.execute(self._container, command)

    def ssh(self):
        self._docker.ssh(self._container)

    @property
    def name(self):
        return self._docker.principal_container_name(self._container)

    @property
    def ip(self):
        return self._docker.container_ip(self._container)

    @property
    def image(self):
        return self._container['Image']

    def ports(self, pretty=False):
        ports = self._container['Ports']

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

        if pretty:
            return __format_ports(ports)

        return ports

    @property
    def service_name(self):
        return '_'.join(self.name.split('_')[1:])
