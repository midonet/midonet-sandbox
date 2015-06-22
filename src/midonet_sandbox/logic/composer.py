# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

from midonet_sandbox.assets.assets import Assets


class Composer(object):
    """
    """

    def __init__(self):
        self._assets = Assets()

    def list_flavours(self):
        return self._assets.get_composer_flavours()