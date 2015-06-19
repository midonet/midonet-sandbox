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

    def build(self, dockerfile, tag):
        log.info('Invoking docker build on {}'.format(dockerfile))

        response = self._client.build(path=os.path.dirname(dockerfile), tag=tag,
                                      dockerfile=os.path.basename(dockerfile))

        for line in response:
            log.info(line)
