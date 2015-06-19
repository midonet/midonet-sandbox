# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from midonet_sandbox.docker_proxy import Docker
from midonet_sandbox.assets.assets import Assets
from configuration import Config

log = logging.getLogger('midonet-sandbox.builder')


class Builder(object):
    """
    Build and optionally publish a docker image
    """

    def __init__(self):
        configuration = Config.Instance()
        self._docker = Docker(configuration.get_default_value('docker_socket'))
        self._assets = Assets()

    def build(self, image, tag='master', publish=False):
        """
        Build and optionally publish a docker image
        :param image: the image to build, eg "midonet"
        :param tag: the tag to apply
        :param publish: true if the image has to be published upstream
        :return:
        """
        log.info('Building {}:{}, publish is {}'.format(image, tag, publish))

        # Build the base image first
        if tag != "base":
            base_dockerfile = self._assets.get_abs_image_dockerfile(image,
                                                                    'base')
            self._docker.build(base_dockerfile, 'base')

        # Build the actual image
        dockerfile = self._assets.get_abs_image_dockerfile(image, tag)
        self._docker.build(dockerfile, tag)

        # TODO - publication