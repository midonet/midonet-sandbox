# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura


from injector import inject, provides, Module, Injector, singleton
from midonet_sandbox.configuration import Config
from midonet_sandbox.wrappers.docker_wrapper import Docker


class SandboxModule(Module):
    def __init__(self, options):
        self._options = options

    @singleton
    @provides(Config)
    def configuration_provider(self):
        return Config(self._options['--config'])

    @singleton
    @provides(Docker)
    @inject(configuration=Config)
    def docker_provider(self, configuration):
        return Docker(configuration.get_sandbox_value('docker_socket'),
                      configuration.get_sandbox_value('docker_remove_intermediate'),
                      configuration.get_sandbox_value('docker_registry'),
                      configuration.get_sandbox_value('docker_insecure_registry'))


def get_injector(options):
    return Injector([SandboxModule(options)])
