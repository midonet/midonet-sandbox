# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

import os

from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.wrappers.composer_wrapper import DockerComposer


log = logging.getLogger('midonet-sandbox.configuration')


class Composer(object):
    """
    """

    def __init__(self):
        self._assets = Assets()
        self._composer = DockerComposer()

    def list_flavours_files(self):
        return self._assets.get_composer_flavours()

    def list_flavours(self):
        return [os.path.splitext(flavour)[0] for flavour in
                self.list_flavours_files()]

    def run(self, flavour):
        log.info('Spawning {} sandbox'.format(flavour))

        if flavour not in self.list_flavours():
            log.error('Cannot find flavour {}. Aborted'.format(flavour))
            return