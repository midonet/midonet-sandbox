# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

import logging
from datetime import datetime

import humanize
from docopt import docopt
from tabulate import tabulate
from midonet_sandbox.assets.assets import BASE_ASSETS_PATH, Assets
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.composer import Composer
from midonet_sandbox.utils import configure_logging
from midonet_sandbox.wrappers.docker_wrapper import Docker

cli = """Midonet Sandbox Manager

Usage:
    sandbox-manage [options] build <image>... [--publish]
    sandbox-manage [options] build-all <flavour> [--force]
    sandbox-manage [options] run <flavour> --name=<name> [--override=<override>] [--force]
    sandbox-manage [options] stop <name>... [--remove]
    sandbox-manage [options] stop-all [--remove]
    sandbox-manage [options] flavours-list [--details]
    sandbox-manage [options] images-list
    sandbox-manage [options] sandbox-list [--details] [--name=<name>]

Options:
    -h --help                       show this screen
    --debug                         debug mode
    -c <config>, --config=<config>  configuration file [default: ~/.midonet-sandboxrc]
"""

_ACTIONS_ = (
    'build', 'build-all', 'run', 'stop', 'stop-all', 'flavours-list',
    'images-list', 'sandbox-list')

log = logging.getLogger('midonet-sandbox.main')


def main():
    options = docopt(cli)

    if options['--debug']:
        configure_logging('debug')
    else:
        configure_logging('info')

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


def build_all(options):
    flavour = options['<flavour>']
    force = options['--force']

    Builder().build_all(flavour, force_rebuild=force)


def flavours_list(options):
    assets = Assets()
    details = options['--details']

    flavours = list()
    for flavour in assets.list_flavours():
        if details:
            components = Composer().get_components_by_flavour(flavour)
            components = ', '.join(['{}x {}'.format(count, image)
                                    for image, count in components.items()])
            flavours.append([flavour, components])
        else:
            flavours.append([flavour])

    if flavours:
        headers = ['Flavours']
        if details:
            headers = ['Flavour', 'Components']

        print(tabulate(flavours, headers=headers, tablefmt='psql'))
        return

    log.info('No flavours found')


def run(options):
    flavour = options['<flavour>']
    name = options['--name']
    force = options['--force']
    override = options['--override']

    if Composer().run(flavour, name, force, override):
        print_sandbox_details([name])


def stop(options):
    names = options['<name>']
    remove = options['--remove']

    Composer().stop(names, remove)


def stop_all(options):
    remove = options['--remove']
    composer = Composer()

    composer.stop(composer.list_running_sandbox(), remove)


def images_list(options):
    docker = Docker(Config.instance_or_die().get_sandbox_value('docker_socket'))
    images = list()

    for image in docker.list_images('sandbox/'):
        images.append([','.join(image['RepoTags']),
                       humanize.naturaltime(
                           datetime.now() -
                           datetime.fromtimestamp(image['Created']))])

    if images:
        print(tabulate(images, headers=['Image', 'Created'], tablefmt='psql'))
        return

    log.info('No images found')


def sandbox_list(options):
    composer = Composer()
    details = options['--details']
    name = options['--name']
    sandboxes = list()

    if not name:
        running_sandboxes = composer.list_running_sandbox()
    else:
        running_sandboxes = [sandbox for sandbox in
                             composer.list_running_sandbox() if sandbox == name]

    if details:
        print_sandbox_details(running_sandboxes)
        return

    for sandbox in running_sandboxes:
        sandboxes.append([sandbox])

    if sandboxes:
        print(tabulate(sandboxes, headers=['Sandbox'], tablefmt='psql'))


def print_sandbox_details(sandboxes):
    sandbox_list = list()

    for sandbox in sandboxes:
        for container in Composer().get_sandbox_detail(sandbox):
            sandbox_list.append(container)

    if sandbox_list:
        headers = ['Sandbox', 'Name', 'Image', 'Ports', 'Ip']
        print(tabulate(sandbox_list, headers=headers, tablefmt='psql'))
