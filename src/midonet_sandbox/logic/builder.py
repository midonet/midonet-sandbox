# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from injector import inject, singleton

from midonet_sandbox.wrappers.docker_wrapper import Docker
from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.exceptions import ImageNotFound
from midonet_sandbox.logic.composer import Composer

log = logging.getLogger('midonet-sandbox.builder')


@singleton
class Builder(object):
    """
    Build and optionally publish a docker image
    """

    @inject(docker=Docker, composer=Composer, assets=Assets)
    def __init__(self, docker, composer, assets):
        self._docker = docker
        self._assets = assets
        self._composer = composer

    def build(self, image):
        """
        Build and optionally publish a docker image
        :param image: the image to build, eg "midolman:1.9"
        :param publish: true if the image has to be published upstream
        :return:
        """
        log.info('Build started for {}'.format(image))

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

    def build_all(self, flavour, force_rebuild):
        components = self._composer.get_components_by_flavour(flavour)
        components = components.keys()
        components = [c.replace('sandbox/', '') for c in components]
        images = [','.join(image['RepoTags']).replace('sandbox/', '') for image
                  in self._docker.list_images('sandbox/')]

        if components:
            log.info('Building the following components: '
                     '{}'.format(', '.join(components)))

            for image in components:
                if (image not in images) or force_rebuild:
                    self.build(image)
                else:
                    log.info('{} image alredy exists. Skipping'.format(image))
