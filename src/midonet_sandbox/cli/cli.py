# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import argparse

from midonet_sandbox.configuration import Config
from midonet_sandbox.logging_core import configure_logging


def cli():
    parser = argparse.ArgumentParser(description="Midonet Sandbox")
    parser.add_argument('-c', '--config', action='store', dest='config',
                        metavar='CONFIGURATION_FILE',
                        help='Configuration file, default: {} '.format(
                            Config.DEFAULT_CONFIGURATION_FILE
                        ))
    parser.add_argument('-l', '--log', action='store', dest='loglevel',
                        metavar='LOG LEVEL', default='INFO')

    return parser.parse_args()


def main():
    args = cli()

    configure_logging(args.loglevel)

    if args.config:
        config = Config(args.config)
    else:
        config = Config()