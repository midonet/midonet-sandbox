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
    pass


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


class TestBuilder(object):
    """
    """

    def setup_method(self, method):
        self.injector = Injector([SandboxModuleTest()])
        self.dispatcher = self.injector.get(Dispatcher)
        self.builder = self.injector.get(Builder)
        self._composer = self.injector.get(Composer)

        self._build = Mock()
        self.builder.build = self._build
        self.builder._composer = self._composer

    def test_build_not_sandbox_image(self):
        images = ['external1', 'sandbox/internal1']
        calls = ['internal1:master']

        options = {
            '<flavour>': 'with_external_component',
            '--force': True
        }

        self.dispatcher.build_all(options)
        for call in calls:
            self._build.assert_any_call(call)

        assert mock.call('external1') not in self._build.mock_calls

if __name__ == '__main__':
    pytest.main()
