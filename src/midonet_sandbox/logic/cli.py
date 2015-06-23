# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging

from docopt import docopt
from midonet_sandbox.assets.assets import BASE_ASSETS_PATH, Assets
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.composer import Composer
from midonet_sandbox.utils import configure_logging


cli = """Midonet Sandbox Manager

Usage:
    sandbox-manage [options] build <image>... [--publish]
    sandbox-manage [options] run <flavour> --name=<name> [--override=<override>]
    sandbox-manage [options] flavours-list

Options:
    -h --help                       show this screen
    -l <level>, --log=<level>       verbose mode [default: INFO]
    -c <config>, --config=<config>  configuration file [default: ~/.midonet-sandboxrc]
"""

_ACTIONS_ = ('build', 'run', 'flavours-list')

log = logging.getLogger('midonet-sandbox.main')


def main():
    options = docopt(cli)

    configure_logging(options['--log'])
    Config.instance(options['--config'])

    log.debug('Base assets directory: {}'.format(BASE_ASSETS_PATH))

    for action in _ACTIONS_:
        if options[action]:
            action = action.replace('-', '_')
            globals()[action](options)
            break


def build(options):
    images = options['<image>']
    publish = options['--publish']

    for image in images:
        if ':' not in image:
            image = '{}:master'.format(image)

        Builder().build(image, publish)


def flavours_list(options):
    print '\n Available flavours: '
    for flavour in Assets().list_flavours():
        print "* {}".format(flavour)


def run(options):
    flavour = options['<flavour>']
    name = options['--name']

    Composer().run(flavour, name)