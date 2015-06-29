# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

import os
from midonet_sandbox import assets
from midonet_sandbox.configuration import Config
from midonet_sandbox.exceptions import ImageNotFound, FlavourNotFound


BASE_ASSETS_PATH = os.path.dirname(assets.__file__)

log = logging.getLogger('midonet-sandbox.assets')


class Assets(object):
    """
    """

    def __init__(self):
        self._config = Config.instance_or_die()

    def get_image_path(self, image, tag):
        path = os.path.join(BASE_ASSETS_PATH, 'images', image, tag)
        if not os.path.isdir(path):
            raise ImageNotFound('Image path does not exist: {}'.format(path))
        return path

    def get_abs_base_components_path(self):
        return os.path.join(BASE_ASSETS_PATH, 'composer', 'base')

    def get_abs_image_dockerfile(self, image, tag):
        abs_image_path = os.path.join(self.get_image_path(image, tag),
                                      '{}-{}.dockerfile'.format(image, tag))

        if not os.path.isfile(abs_image_path):
            raise ImageNotFound(
                'Image file not found: {}'.format(abs_image_path))

        return abs_image_path

    def list_flavours_files(self):
        flavours = list()

        package_path = os.path.join(BASE_ASSETS_PATH, 'composer', 'flavours')
        flavours.extend([yml for yml in os.listdir(package_path) if
                         yml.lower().endswith('.yml')])

        extra_path = self._config.get_sandbox_value('extra_flavours')
        if extra_path:
            if os.path.isdir(extra_path):
                flavours.extend(
                    [yml for yml in os.listdir(extra_path) if
                     yml.endswith('.yml')])
            else:
                log.warning(
                    'Ignoring {}. Not a valid directory'.format(extra_path))

        return set(flavours)

    def list_flavours(self):
        return [os.path.splitext(flavour)[0] for flavour in
                self.list_flavours_files()]

    def get_flavours_paths(self):
        extra_flavours = self._config.get_sandbox_value('extra_flavours')
        flavour_paths = [os.path.join(BASE_ASSETS_PATH, 'composer', 'flavours')]

        if extra_flavours and os.path.isdir(extra_flavours):
            flavour_paths = [extra_flavours,
                             os.path.join(BASE_ASSETS_PATH, 'composer',
                                          'flavours')]

        return flavour_paths

    def get_abs_flavour_path(self, flavour):
        if not flavour.endswith('.yml'):
            flavour = '{}.yml'.format(flavour)

        flavour_file = None
        for path in self.get_flavours_paths():
            flavour_file = os.path.join(path, flavour)
            if os.path.isfile(flavour_file):
                break

        if not flavour_file or not os.path.isfile(flavour_file):
            raise FlavourNotFound('Flavour not found: {}'.format(flavour_file))

        return flavour_file

    def get_components_by_flavour(self, flavour):

        flavour_path = self.get_abs_flavour_path(flavour)

        # TODO: Complete
        return 'cassandra'
