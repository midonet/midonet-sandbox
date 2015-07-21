# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

from mock import Mock

import pytest
from midonet_sandbox.logic.cli import _find_action, dispatch


class MockDispatcher():
    pass


class TestCli(object):
    """
    """

    def setup_method(self, method):
        self.options = {
            'a': False,
            'b': False,
            'exec': False,  # keyword
            'test-action': False,  # '-' action
            'invoke': False,
            '-invoke': False
        }

        self.dispatcher = MockDispatcher()

    def _assert_find_action(self, action, expected):
        self.options[action] = True

        action = _find_action(self.options)

        assert action == expected

    def test_find_action_keywords(self):
        self._assert_find_action('exec', 'exec_')

    def test_find_action_dash(self):
        self._assert_find_action('test-action', 'test_action')

    def test_actions_call(self):
        self.options['invoke'] = True

        invoke = Mock()
        self.dispatcher.invoke = invoke

        dispatch(self.options, self.dispatcher)

        invoke.assert_called_once_with(self.options)

    def test_only_call_actions(self):
        self.options['-invoke'] = True

        invoke = Mock()
        self.dispatcher._invoke = invoke

        dispatch(self.options, self.dispatcher)

        invoke.assert_not_called()


if __name__ == '__main__':
    pytest.main()
