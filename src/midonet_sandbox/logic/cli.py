# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
import keyword

from docopt import docopt
import sys
from midonet_sandbox.logic.injection import get_injector
from midonet_sandbox.assets.assets import BASE_ASSETS_PATH
from midonet_sandbox.logic.dispatcher import Dispatcher
from midonet_sandbox.utils import configure_logging

command_line = """Midonet Sandbox Manager

Usage:
    sandbox-manage [options] build <image>... [--force]
    sandbox-manage [options] build-all <flavour> [--force]
    sandbox-manage [options] pull <image>...
    sandbox-manage [options] pull-all <flavour>
    sandbox-manage [options] push <image>...
    sandbox-manage [options] push-all <flavour>
    sandbox-manage [options] run <flavour> --name=<name> [--override=<override>] [--provision=<script>] [--force] [--no-recreate] [--verbose]
    sandbox-manage [options] stop <name>... [--remove]
    sandbox-manage [options] stop-all [--remove]
    sandbox-manage [options] kill <name>... [--remove]
    sandbox-manage [options] kill-all [--remove]
    sandbox-manage [options] exec <container> <command>
    sandbox-manage [options] ssh <container>
    sandbox-manage [options] flavours-list [--details]
    sandbox-manage [options] images-list
    sandbox-manage [options] sandbox-list [--details] [--name=<name>]

Options:
    -h --help                       show this screen
    --debug                         debug mode
    -c <config>, --config=<config>  configuration file [default: ~/.midonet-sandboxrc]
"""

log = logging.getLogger('midonet-sandbox.main')


def main():
    options = docopt(command_line)
    injector = get_injector(options)
    dispatcher = injector.get(Dispatcher)

    if not dispatch(options, dispatcher):
        sys.exit(1)


def dispatch(options, dispatcher):
    if '--debug' in options:
        if options['--debug']:
            configure_logging('debug')
        else:
            configure_logging('info')

    log.debug('Base assets directory: {}'.format(BASE_ASSETS_PATH))

    action = _find_action(options)
    if action and hasattr(dispatcher, action):
        return getattr(dispatcher, action)(options)



def _find_action(options):
    actions = \
        filter(lambda opt: not opt.startswith('<') and not opt.startswith('-'),
               options.keys())

    for action in actions:
        if options[action]:
            action = action.replace('-', '_')
            if keyword.iskeyword(action):
                action = '{}_'.format(action)
            return action


if __name__ == '__main__':
    main()
