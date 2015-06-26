# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura


import os
from midonet_sandbox import assets
from midonet_sandbox.exceptions import ImageNotFound, FlavourNotFound

BASE_ASSETS_PATH = os.path.dirname(assets.__file__)


class Assets(object):
    """
    """

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

    def list_flavours_files(self):
        path = os.path.join(BASE_ASSETS_PATH, 'composer', 'flavours')
        return os.listdir(path)

    def list_flavours(self):
        return [os.path.splitext(flavour)[0] for flavour in
                self.list_flavours_files()]

    def get_flavours_path(self):
        return os.path.join(BASE_ASSETS_PATH, 'composer', 'flavours')

    def get_abs_flavour_path(self, flavour):
        if not flavour.endswith('.yml'):
            flavour = '{}.yml'.format(flavour)

        flavour_file = os.path.join(self.get_flavours_path(), flavour)

        if not os.path.isfile(flavour_file):
            raise FlavourNotFound('Flavour not found: {}'.format(flavour_file))

        return flavour_file

    def get_components_by_flavour(self, flavour):

        flavour_path = self.get_abs_flavour_path(flavour)

        # TODO: Complete
        return 'cassandra'