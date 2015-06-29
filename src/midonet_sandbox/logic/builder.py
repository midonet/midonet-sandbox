# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from midonet_sandbox.wrappers.docker_wrapper import Docker
from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.exceptions import ImageNotFound
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.composer import Composer

log = logging.getLogger('midonet-sandbox.builder')


class Builder(object):
    """
    Build and optionally publish a docker image
    """

    def __init__(self):
        configuration = Config.instance_or_die()
        self._docker = Docker(configuration.get_sandbox_value('docker_socket'))
        self._assets = Assets()
        self._composer = Composer()

    def build(self, image, publish=False):
        """
        Build and optionally publish a docker image
        :param image: the image to build, eg "midolman:1.9"
        :param publish: true if the image has to be published upstream
        :return:
        """
        log.info('Build started for {}, publish is {}'.format(image, publish))

        name, tag = image.split(':')

        # Build the base image first if exists
        if tag != 'base':
            try:
                base_dockerfile = self._assets.get_abs_image_dockerfile(name,
                                                                        'base')
                self._docker.build(base_dockerfile,
                                   'sandbox/{}:base'.format(name))
            except ImageNotFound:
                log.info('Base image {}:base not found, skipping'.format(name))

        # Build the actual image
        try:
            dockerfile = self._assets.get_abs_image_dockerfile(name, tag)
            self._docker.build(dockerfile, 'sandbox/{}'.format(image))
        except ImageNotFound:
            log.error('Image {} not found, build aborted'.format(image))

            # TODO - publication

    def build_all(self, flavour):
        components = self._composer.get_components_by_flavour(flavour)
        components = components.keys()
        components = [c.replace('sandbox/', '') for c in components]

        log.info('Building the following components: '
                 '{}'.format(', '.join(components)))

        for image in components:
            self.build(image)
