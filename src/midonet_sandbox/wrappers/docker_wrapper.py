# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

import os
from docker import Client

log = logging.getLogger('midonet-sandbox.docker')


class Docker(object):
    def __init__(self, socket):
        log.debug('DockerClient connecting to {}'.format(socket))
        self._client = Client(base_url=socket)

    def build(self, dockerfile, image):
        """/
        :param dockerfile: The dockerfile full path
        :param image: the image name (eg: midolman:1.9)
        """
        log.info('Now building {}'.format(image))
        log.debug('Invoking docker build on {}'.format(dockerfile))

        response = self._client.build(path=os.path.dirname(dockerfile),
                                      tag=image, pull=False, rm=True,
                                      dockerfile=os.path.basename(dockerfile))

        for line in response:
            print eval(line)['stream'],


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