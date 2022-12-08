"""
This module tests the bahaviourof the endpoint class and the construction of endpoint hierarchy
trees. It doesn't test the actual API calls.
"""

import pytest

from boum.api_client.v1.endpoint import Endpoint


class EndpointAC(Endpoint):
    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "EndpointAC":
        return super().__get__(instance, owner)


class EndpointA(Endpoint):
    endpoint_c = EndpointAC('c')

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "EndpointA":
        return super().__get__(instance, owner)


class EndpointBD(Endpoint):
    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "EndpointBD":
        return super().__get__(instance, owner)


class EndpointB(Endpoint):
    endpoint_d = EndpointBD('d', disabled_for_collection=True)

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "EndpointB":
        return super().__get__(instance, owner)

    def get(self):
        return self._get()


class EndpointRoot(Endpoint):
    endpoint_a = EndpointA('a')
    endpoint_b = EndpointB('b')

    # pylint: disable=useless-parent-delegation
    def __get__(self, instance, owner: type) -> "EndpointRoot":
        return super().__get__(instance, owner)


def test__create_without_resource_where_enabled__urls_are_correct():
    root = EndpointRoot('base')
    assert root.url == 'base'
    assert root.endpoint_a.url == 'base/a'
    assert root.endpoint_a.endpoint_c.url == 'base/a/c'
    assert root.endpoint_b.url == 'base/b'


def test__create_without_resource_where_disabled__raises_attribute_error():
    root = EndpointRoot('base')
    with pytest.raises(AttributeError):
        # pylint: disable=pointless-statement
        # noinspection PyStatementEffect
        root.endpoint_b.endpoint_d.url


def test__create_with_resource_ids__urls_are_correct():
    root = EndpointRoot('base')
    assert root.endpoint_a('1').url == 'base/a/1'
    assert root.endpoint_a.endpoint_c('2').url == 'base/a/c/2'
    assert root.endpoint_a('3').endpoint_c('4').url == 'base/a/3/c/4'
    assert root.endpoint_b('5').endpoint_d('6').url == 'base/b/5/d/6'


def test__request_attempt_with_not_connected_endpoint__raises_runtime_error():
    root = EndpointRoot('base')
    # noinspection PyTypeChecker
    root.set_session(None)
    with pytest.raises(RuntimeError):
        root.endpoint_b('1').get()
