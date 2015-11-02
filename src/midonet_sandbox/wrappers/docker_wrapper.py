# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
import subprocess

import os
from docker import Client
from requests.exceptions import ConnectionError
from midonet_sandbox.utils import exception_safe

log = logging.getLogger('midonet-sandbox.docker')


class Docker(object):
    def __init__(self, socket, remove_intermediate=False):
        log.debug('DockerClient connecting to {}'.format(socket))
        self._socket = socket
        self._client = Client(base_url=socket)
        self._remove_intermediate = remove_intermediate

    @exception_safe(ConnectionError, None)
    def build(self, dockerfile, image):
        """/
        :param dockerfile: The dockerfile full path
        :param image: the image name (eg: midolman:1.9)
        """
        log.info('Now building {}'.format(image))
        log.debug('Invoking docker build on {}'.format(dockerfile))

        response = self._client.build(path=os.path.dirname(dockerfile),
                                      tag=image, pull=False,
                                      rm=self._remove_intermediate,
                                      dockerfile=os.path.basename(dockerfile))

        for line in response:
            eval_line = eval(line)
            if 'stream' in eval_line:
                print(eval_line['stream']),

    @exception_safe(ConnectionError, [])
    def list_images(self, prefix=None):
        """
        List the available images
        :param prefix: Filter the images by a prefix (eg: "sandbox/")
        :return: the images list
        """
        images = self._client.images()

        if prefix:
            filtered = list()
            for image in images:
                for tag in image['RepoTags']:
                    if tag.startswith(prefix):
                        filtered.append(image)

            images = filtered

        return images

    def list_containers(self, prefix=None):
        """
        List the running containers, prefixed with prefix
        :param prefix: The container's name prefix
        :return: The list of containers
        """
        containers = self._client.containers()
        filtered = list()
        if prefix:
            for container_ref in containers:
                if prefix in container_ref['Names'][0]:
                    filtered.append(container_ref)

            containers = filtered

        return containers

    def container_by_name(self, name):
        containers = self.list_containers()
        for container_ref in containers:
            if name == self.principal_container_name(container_ref):
                return container_ref

    @staticmethod
    def principal_container_name(container_ref):
        for name in container_ref['Names']:
            if '/' not in name[1:]:
                return name[1:]

    def container_ip(self, container_ref):
        return self._client.inspect_container(container_ref)['NetworkSettings'][
            'IPAddress']

    def stop_container(self, container_ref):
        self._client.stop(container_ref)

    def remove_container(self, container_ref):
        self._client.remove_container(container_ref)

    @exception_safe(OSError, None)
    def execute(self, container_ref, command):
        """
        Execute a command inside the container.

        NOTE: Needs the 'docker' binary installed in the host
        """
        cmd = ['docker', 'exec', '-it',
               self.principal_container_name(container_ref), command]
        log.debug('Running command: "{}"'.format(' '.join(cmd)))
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        p.wait()

    def ssh(self, container_ref):
        self.execute(container_ref, 'bash')
