# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import argparse

from midonet_sandbox.configuration import Config, DEFAULT_CONFIGURATION_FILE
from midonet_sandbox.logging_core import configure_logging
from midonet_sandbox.builder import Builder


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

    return parser.parse_args()


def main():
    args = cli()

    configure_logging(args.loglevel)

    if args.config:
        Config.Instance(args.config)
    else:
        Config.Instance()

    if args.build:
        builder = Builder()
        if ':' in args.build:
            image, tag = args.build.split(':')
            builder.build(image, tag, args.publish)
        else:
            builder.build(args.build, publish=args.publish)