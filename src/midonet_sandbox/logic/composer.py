# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.wrappers.composer_wrapper import DockerComposer


log = logging.getLogger('midonet-sandbox.configuration')


class Composer(object):
    """
    """

    def __init__(self):
        self._assets = Assets()
        self._composer = DockerComposer()

    def run(self, flavour, name):
        log.info('Spawning {} sandbox'.format(flavour))

        if flavour not in self._assets.list_flavours():
            log.error('Cannot find flavour {}. Aborted'.format(flavour))
            return

        flavour_file = self._assets.get_abs_flavour_path(flavour)

        composer = self._composer.up(flavour_file, name)
        composer.wait()