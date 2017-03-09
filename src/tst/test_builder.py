# Copyright 2015 Midokura SARL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from mock import Mock
import mock
from injector import Injector, singleton, provides

import pytest
from midonet_sandbox.configuration import Config
from midonet_sandbox.logic.builder import Builder
from midonet_sandbox.logic.dispatcher import Dispatcher
from midonet_sandbox.logic.injection import SandboxModule
from midonet_sandbox.wrappers.docker_wrapper import Docker
from midonet_sandbox.logic.composer import Composer


class DockerMock(object):

    def __init__(self):
        self.existing_images = []

    def set_existing_images(self, existing_images):
        self.existing_images = existing_images

    def list_images(self, prefix):
        filtered = list()
        if prefix:
            for image in self.existing_images:
                if 'RepoTags' in image and image['RepoTags'] is not None:
                    for tag in image['RepoTags']:
                        if tag.startswith(prefix):
                            filtered.append(image)
        return filtered


class BuilderMock(object):
    pass


class ComposerMock(object):

    def get_components_by_flavour(self, flavour):
        if flavour is 'with_external_component':
            return {'external1:master': None,
                    'sandbox/internal1:master': None}
        elif flavour is 'without_external_component':
            return {'sandbox/internal1:master': None,
                    'sandbox/internal2:master': None}


class SandboxModuleTest(SandboxModule):
    def __init__(self):
        super(self.__class__, self).__init__(dict())

    @singleton
    @provides(Config)
    def configuration_provider(self):
        return Config('mock')

    @singleton
    @provides(Composer)
    def composer_provider(self):
        return ComposerMock()

    @singleton
    @provides(Docker)
    def docker_provider(self):
        return DockerMock()


class TestBuilder(object):
    """
    """

    def setup_method(self, method):
        self.injector = Injector([SandboxModuleTest()])
        self.dispatcher = self.injector.get(Dispatcher)
        self.builder = self.injector.get(Builder)
        self._composer = self.injector.get(Composer)
        self._docker = self.injector.get(Docker)

        self._build = Mock()
        self.builder.build = self._build
        self.builder._composer = self._composer

    def test_build_not_sandbox_image(self):
        options = {
            '<flavour>': 'with_external_component',
            '--force': False
        }

        self.dispatcher.build_all(options)
        self._build.assert_called_once_with(u'internal1:master')

    def test_existing_image_not_build(self):
        exists = [{'RepoTags': ['sandbox/internal1:master']}]

        options = {
            '<flavour>': 'without_external_component',
            '--force': False
        }
        self._docker.set_existing_images(exists)

        self.dispatcher.build_all(options)
        self._build.assert_called_once_with(u'internal2:master')

    def test_existing_image_not_build_with_extra_tag(self):
        exists = [{'RepoTags': ['sandbox/internal1:master',
                                'repo/sandbox/internal1:master']}]

        options = {
            '<flavour>': 'without_external_component',
            '--force': False
        }
        self._docker.set_existing_images(exists)

        self.dispatcher.build_all(options)
        self._build.assert_called_once_with(u'internal2:master')

    def test_force_build_existing_image(self):
        exists = [{'RepoTags': ['sandbox/internal1:master',
                                'repo/sandbox/internal1:master']}]

        options = {
            '<flavour>': 'without_external_component',
            '--force': True
        }
        self._docker.set_existing_images(exists)

        self.dispatcher.build_all(options)
        self._build.assert_has_calls([mock.call(u'internal1:master'),
                                      mock.call(u'internal2:master')],
                                     any_order=True)


if __name__ == '__main__':
    pytest.main()
