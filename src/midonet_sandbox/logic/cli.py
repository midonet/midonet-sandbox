# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import argparse

import os
from midonet_sandbox.configuration import Config, DEFAULT_CONFIGURATION_FILE
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.composer import Composer
from midonet_sandbox.utils import configure_logging


def cli():
    parser = argparse.ArgumentParser(description="Midonet Sandbox")
    parser.add_argument('-c', '--config', action='store', dest='config',
                        metavar='CONFIGURATION_FILE',
                        help='Configuration file, default: {} '.format(
                            DEFAULT_CONFIGURATION_FILE
                        ))
    parser.add_argument('-l', '--log', action='store', dest='loglevel',
                        metavar='LOG LEVEL', default='INFO')

    parser.add_argument('-b', '--build', action='store', dest='build',
                        metavar='component:version',
                        help='The component to build')

    parser.add_argument('-p', '--publish', action='store_true', dest='publish',
                        help='Publish the image upstream')

    parser.add_argument('-r', '--run', action='store', dest='run',
                        help='Run a specific flavour')

    parser.add_argument('--list', action='store_true', dest='list',
                        help='List flavours')

    return parser.parse_args()


def main():
    args = cli()

    configure_logging(args.loglevel)

    if args.config:
        Config.Instance(args.config)
    else:
        Config.Instance()

    if args.build:
        image = args.build
        builder = Builder()
        if ':' in args.build:
            builder.build(image, args.publish)
        else:
            builder.build('{}:master'.format(image), publish=args.publish)

    elif args.list:
        composer = Composer()
        print 'Available flavours: '
        for flavour in composer.list_flavours():
            print "* {}".format(os.path.splitext(flavour)[0])