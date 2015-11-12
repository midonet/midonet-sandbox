# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura
import logging
from datetime import datetime

import humanize
from tabulate import tabulate
from injector import inject, singleton
from midonet_sandbox.assets.assets import Assets
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.composer import Composer
from midonet_sandbox.logic.container import ContainerBuilder
from midonet_sandbox.wrappers.docker_wrapper import Docker

log = logging.getLogger('midonet-sandbox.cli')


@singleton
class Dispatcher(object):

    @inject(builder=Builder, assets=Assets, composer=Composer, config=Config,
            container_builder=ContainerBuilder)
    def __init__(self, builder, assets, composer, config, container_builder):
        self._builder = builder
        self._assets = assets
        self._composer = composer
        self._config = config
        self._container_builder = container_builder

    def build(self, options):
        images = options['<image>']

        for image in images:
            if ':' not in image:
                image = '{}:master'.format(image)

            if not self._builder.build(image):
                return False
        return True

    def build_all(self, options):
        flavour = options['<flavour>']
        force = options['--force']

        return self._builder.build_all(flavour, force_rebuild=force)

    def pull(self, options):
        images = options['<image>']
        for image in images:
            if ':' not in image:
                image = '{}:master'.format(image)

            if not self._builder.pull(image):
                return False
        return True

    def pull_all(self, options):
        flavour = options['<flavour>']

        return self._builder.pull_all(flavour)

    def push(self, options):
        images = options['<image>']
        for image in images:
            if ':' not in image:
                image = '{}:master'.format(image)

            if not self._builder.push(image):
                return False
        return True

    def push_all(self, options):
        flavour = options['<flavour>']

        return self._builder.push_all(flavour)

    def flavours_list(self, options):
        details = options['--details']

        flavours = list()
        for flavour in self._assets.list_flavours():
            if details:
                components = self._composer.get_components_by_flavour(flavour)
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
            return True

        log.info('No flavours found')
        return True

    def run(self, options):
        flavour = options['<flavour>']
        name = options['--name']
        force = options['--force']
        override = options['--override']
        provision = options['--provision']

        if self._composer.run(flavour, name, force, override, provision):
            self.print_sandbox_details([name])
            return True
        return False

    def stop(self, options):
        names = options['<name>']
        remove = options['--remove']

        return self._composer.stop(names, remove)

    def stop_all(self, options):
        remove = options['--remove']
        composer = self._composer

        return composer.stop(composer.list_running_sandbox(), remove)

    def exec_(self, options):
        container = self._container_builder.for_name(options['<container>'])
        command = options['<command>']

        if container:
            container.execute(command)

    def ssh(self, options):
        container = self._container_builder.for_name(options['<container>'])
        if container:
            container.ssh()

    def images_list(self, options):
        docker = Docker(self._config.get_sandbox_value('docker_socket'),
                        self._config.get_sandbox_value('docker_remove_intermediate'))
        images = list()

        for image in docker.list_images('sandbox/'):
            images.append([','.join(image['RepoTags']),
                           humanize.naturaltime(
                               datetime.now() -
                               datetime.fromtimestamp(image['Created']))])

        if images:
            print(
                tabulate(images, headers=['Image', 'Created'], tablefmt='psql'))
            return True

        log.info('No images found')
        return False

    def sandbox_list(self, options):
        details = options['--details']
        name = options['--name']
        sandboxes = list()

        if not name:
            running_sandboxes = self._composer.list_running_sandbox()
        else:
            running_sandboxes = [sandbox for sandbox in
                                 self._composer.list_running_sandbox() if
                                 sandbox == name]

        if details:
            self.print_sandbox_details(running_sandboxes)

        for sandbox in running_sandboxes:
            sandboxes.append([sandbox])

        if sandboxes:
            print(tabulate(sandboxes, headers=['Sandbox'], tablefmt='psql'))

        return True

    def print_sandbox_details(self, sandboxes):
        sandbox_list = list()

        for sandbox in sandboxes:
            for container in self._composer.get_sandbox_detail(sandbox):
                sandbox_list.append(container)

        if sandbox_list:
            headers = ['Sandbox', 'Name', 'Image', 'Ports', 'Ip']
            print(tabulate(sandbox_list, headers=headers, tablefmt='psql'))

        return True
