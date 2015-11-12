# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura
from mock import Mock
from injector import Injector, singleton, provides

import pytest
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.dispatcher import Dispatcher
from midonet_sandbox.logic.injection import SandboxModule
from midonet_sandbox.wrappers.docker_wrapper import Docker


class DockerMock(object):
    pass


class BuilderMock(object):
    pass


class SandboxModuleTest(SandboxModule):
    def __init__(self):
        super(self.__class__, self).__init__(dict())

    @singleton
    @provides(Config)
    def configuration_provider(self):
        return Config('mock')

    @singleton
    @provides(Docker)
    def docker_provider(self, *args):
        return DockerMock()

    @singleton
    @provides(Builder)
    def builder_provider(self):
        return BuilderMock()


class TestDispatcher(object):
    """
    """

    def setup_method(self, method):
        self.injector = Injector([SandboxModuleTest()])
        self.dispatcher = self.injector.get(Dispatcher)

        if method.__name__.startswith('test_build'):
            self._build = Mock()
            self._build_all = Mock()
            self.builder = self.injector.get(Builder)
            self.builder.build = self._build
            self.builder.build_all = self._build_all

    def _assert_build_call(self, images, calls):
        options = {
            '<image>': images
        }
        self.dispatcher.build(options)

        for call in calls:
            self._build.assert_any_call(call)

    # test build action
    def test_build_no_tag(self):
        images = ['sandbox/test']
        calls = ['sandbox/test:master']

        self._assert_build_call(images, calls)

    def test_build_tag(self):
        images = ['sandbox/test:1.0']
        calls = ['sandbox/test:1.0']

        self._assert_build_call(images, calls)

    def test_build_multiple_images(self):
        images = ['sandbox/image1:1.0', 'sandbox/image2']
        calls = ['sandbox/image1:1.0', 'sandbox/image2:master']

        self._assert_build_call(images, calls)

    # test build_all action
    def test_build_all_force(self):
        options = {
            '<flavour>': 'test',
            '--force': True
        }

        self.dispatcher.build_all(options)

        self._build_all.assert_called_once_with('test', force_rebuild=True)

    def test_build_all_no_force(self):
        options = {
            '<flavour>': 'test',
            '--force': False
        }

        self.dispatcher.build_all(options)

        self._build_all.assert_called_once_with('test', force_rebuild=False)


if __name__ == '__main__':
    pytest.main()
