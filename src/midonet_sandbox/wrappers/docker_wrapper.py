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

    def __init__(self, socket, remove_intermediate=False, registry=None,
                 insecure_registry=False):
        log.debug('DockerClient connecting to {}'.format(socket))
        self._socket = socket
        self._client = Client(base_url=socket, timeout=300, version='auto')
        self._remove_intermediate = remove_intermediate
        self._registry = registry
        self._insecure_registry = insecure_registry

    @exception_safe(ConnectionError, False)
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

        last_line = None
        for line in response:
            eval_line = eval(line)
            if 'stream' in eval_line:
                print(eval_line['stream']),
                last_line = eval_line['stream']
        # Check for ensure success after building
        if 'Successfully built' not in last_line:
            log.error('Error building the image {}.'.format(image))
            return False
        return True

    @exception_safe(ConnectionError, None)
    def pull(self, image):
        """
        :param image: The image name with its tag
        :param repository: The repository where to pull the image
                          (dockerhub if none defined)
        """
        name, tag = image.split(':')
        repository = '{}/{}'.format(self._registry, name) \
            if self._registry else name
        log.info('Now Pulling {}:{}'.format(repository, tag))
        response = self._client.pull(repository=repository,
                                     tag=tag,
                                     insecure_registry=self._insecure_registry,
                                     stream=True)
        for line in response:
            eval_line = eval(line)
            if 'error' in eval_line:
                log.error(
                    'Error pulling image: {}'.format(eval_line['error']))
                return False
            if 'status' in eval_line:
                log.info('[{}:{}] Status: {}'.format(repository,
                                                     tag,
                                                     eval_line['status']))
        if self._registry:
            # If pulling from an external repo, we need to tag with the
            # actual image name used in the flavours definition.
            images = self.list_images(repository)
            for image in images:
                for repotag in image['RepoTags']:
                    if '{}:{}'.format(repository, tag) == repotag:
                        self._client.tag(image['Id'], name, tag, force=True)
        return True

    @exception_safe(ConnectionError, None)
    def push(self, image):
        """
        :param image: The image name with its tag
        :param repository: The repository where to push the image
                           (dockerhub if none defined)
        """
        name, tag = image.split(':')
        if self._registry:
            # First tag the local image to map to the new registry
            repository = '{}/{}'.format(self._registry, name)
            images = self.list_images(name)
            for image in images:
                for repotag in image['RepoTags']:
                    if '{}:{}'.format(name, tag) == repotag:
                        self._client.tag(image['Id'], repository, tag,
                                         force=True)
        else:
            repository = name
        log.info('Now pushing {}:{}'.format(repository, tag))
        response = self._client.push(repository=repository,
                                     tag=tag,
                                     insecure_registry=self._insecure_registry,
                                     stream=True)
        for line in response:
            eval_line = eval(line)
            if 'error' in eval_line:
                log.error(
                    'Error pushing image: {}'.format(eval_line['error'])
                )
                return False
            if 'status' in eval_line:
                if 'Pushing' not in eval_line['status'] \
                        and 'Buffering' not in eval_line['status']:
                    log.info('[{}:{}] Status: {}'.format(repository,
                                                         tag,
                                                         eval_line['status']))
        return True

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
        return self._client.inspect_container(
            container_ref
        )['NetworkSettings']['IPAddress']

    def stop_container(self, container_ref):
        self._client.stop(container_ref)

    def kill_container(self, container_ref):
        self._client.kill(container_ref)

    def remove_container(self, container_ref):
        self._client.remove_container(container_ref)

    @exception_safe(OSError, False)
    def execute(self, container_ref, command):
        """
        Execute a command inside the container.

        NOTE: Needs the 'docker' binary installed in the host
        """
        cmd = ['docker', 'exec', '-it',
               self.principal_container_name(container_ref),
               'env', 'TERM=xterm',
               command]
        log.debug('Running command: "{}"'.format(' '.join(cmd)))
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        p.wait()

    def ssh(self, container_ref):
        self.execute(container_ref, 'bash')
