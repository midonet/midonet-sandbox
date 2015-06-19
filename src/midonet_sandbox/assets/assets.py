# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura


import os
from midonet_sandbox import assets
from midonet_sandbox.exceptions import ImageNotFound

BASE_ASSETS_PATH = os.path.dirname(assets.__file__)


class Assets(object):
    def get_image_path(self, image, tag):
        path = os.path.join(BASE_ASSETS_PATH, 'images', image, tag)
        if not os.path.isdir(path):
            raise ImageNotFound('Image path does not exist: {}'.format(path))
        return path

    def get_abs_image_dockerfile(self, image, tag):
        abs_image_path = os.path.join(self.get_image_path(image, tag),
                                      '{}-{}.dockerfile'.format(image, tag))

        if not os.path.isfile(abs_image_path):
            raise ImageNotFound(
                'Image file not found: {}'.format(abs_image_path))

        return abs_image_path
