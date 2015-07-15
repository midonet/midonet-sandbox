# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from injector import inject
from midonet_sandbox.wrappers.docker_wrapper import Docker
from midonet_sandbox.exceptions import ContainerNotFound
from midonet_sandbox.utils import exception_safe

log = logging.getLogger('midonet-sandbox.container')


class ContainerBuilder(object):
    @inject(docker=Docker)
    def __init__(self, docker):
        self._docker = docker

    def for_name(self, name):
        return Container(self._docker, name=name)

    def for_container_ref(self, container_ref):
        return Container(self._docker, container_ref=container_ref)


class Container(object):
    """
    Simple container operations
    """

    @exception_safe(ContainerNotFound, None)
    def __init__(self, docker, container_ref=None, name=None):

        assert bool(container_ref) ^ bool(name)

        self._docker = docker

        if name:
            container_ref = docker.container_by_name(name)
            if not container_ref:
                raise ContainerNotFound('Container {} not found'.format(name))

        self._container_ref = container_ref

    def execute(self, command):
        self._docker.execute(self._container_ref, command)

    def ssh(self):
        self._docker.ssh(self._container_ref)

    @property
    def name(self):
        return self._docker.principal_container_name(self._container_ref)

    @property
    def ip(self):
        return self._docker.container_ip(self._container_ref)

    @property
    def image(self):
        return self._container_ref['Image']

    def ports(self, pretty=False):
        ports = self._container_ref['Ports']

        def __format_ports(port_list):
            ports_list = list()
            for port in port_list:
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
