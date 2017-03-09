# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import itertools
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
        :return:
        """
        log.info('Build started for {}'.format(image))

        name, tag = image.split(':')

        # Build the base image first if exists
        base_image = self._assets.get_image_base(name, tag)
        if base_image:
            base_name, base_tag = base_image.split(':')
            if base_name.startswith("sandbox/"):
                if not self.build(base_image.replace("sandbox/", "", 1)):
                    log.info(
                        'Base image {} not found, skipping'.format(base_image))
                    return False

        # Build the actual image
        try:
            dockerfile = self._assets.get_abs_image_dockerfile(name, tag)
            return self._docker.build(dockerfile, 'sandbox/{}'.format(image))
        except ImageNotFound:
            log.error('Image {} not found, build aborted'.format(image))
            return False

    def build_all(self, flavour, force_rebuild):
        components = self._composer.get_components_by_flavour(flavour)
        components = components.keys()
        components = [unicode(c.replace('sandbox/', ''), "utf-8")
                      for c in components if 'sandbox/' in c]
        # RepoTags attribute may contain a list of tags
        # (i.e. images with the same sha).
        # Filter those from an remote repo, and keep those with only one /
        tags = [tag.replace('sandbox/', '') for image in
                self._docker.list_images('sandbox/')
                for tag in image['RepoTags'] if tag.count('/') == 1]
        images = ','.join(tag for tag in tags)
        if components:
            log.info('Building the following components: '
                     '{}'.format(', '.join(components)))

            for image in components:
                if (image not in images) or force_rebuild:
                    if not self.build(image):
                        return False
                else:
                    log.info('{} image already exists. Skipping'.format(image))
        return True

    def pull(self, image):
        log.info('Pulling started for {}'.format(image))

        # Pull the actual image
        try:
            return self._docker.pull(image)
        except ImageNotFound:
            log.error('Image {} not found, build aborted'.format(image))

    def pull_all(self, flavour):
        components = self._composer.get_components_by_flavour(flavour)

        if components:
            log.info('Pulling the following images: '
                     '{}'.format(', '.join(components)))
            for image in components:
                if not self.pull(image):
                    return False
        return True

    def push(self, image):
        log.info('Pushing started for {}'.format(image))

        # Push the actual image
        try:
            return self._docker.push(image)
        except:
            log.error('Unknown exception.')
            raise

    def push_all(self, flavour):
        components = self._composer.get_components_by_flavour(flavour)

        if components:
            log.info('Pushing the following images: '
                     '{}'.format(', '.join(components)))
            for image in components:
                if not self.push(image):
                    return False
        return True
