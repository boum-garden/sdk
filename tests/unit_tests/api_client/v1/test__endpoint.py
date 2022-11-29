import pytest

from boum.api_client.v1.endpoint import Endpoint


class EndpointAC(Endpoint):
    pass


class EndpointA(Endpoint):
    endpoint_c = EndpointAC('c')


class EndpointBD(Endpoint):
    pass


class EndpointB(Endpoint):
    endpoint_d = EndpointBD('d', disable_for_collection=True)


class EndpointRoot(Endpoint):
    _path_segment = ''
    endpoint_a = EndpointA('a')
    endpoint_b = EndpointB('b')


def test__create_without_resource_where_enabled__urls_are_correct():
    root = EndpointRoot('base', '/')
    assert root.url == 'base/'
    assert root.endpoint_a.url == 'base/a'
    assert root.endpoint_a.endpoint_c.url == 'base/a/c'
    assert root.endpoint_b.url == 'base/b'

def test__create_without_resource_where_disabled__raises_attribute_error():
    root = EndpointRoot('base', '/')
    with pytest.raises(AttributeError):
        root.endpoint_b.endpoint_d.url

def test__create_with_resource_ids__urls_are_correct():
    root = EndpointRoot('base')
    assert root.endpoint_a('1').url == 'base/a/1'
    assert root.endpoint_a.endpoint_c('2').url == 'base/a/c/2'
    assert root.endpoint_a('3').endpoint_c('4').url == 'base/a/3/c/4'
    assert root.endpoint_b('5').endpoint_d('6').url == 'base/b/5/d/6'


def test__connect_root__all_endpoints_are_connected():
    root = EndpointRoot('base', '/')
    root.connect()

    assert root.is_connected()
    assert root.endpoint_a.is_connected()
    assert root.endpoint_a.endpoint_c.is_connected()
    assert root.endpoint_b.is_connected()
    assert root.endpoint_a('1').is_connected()
    assert root.endpoint_a.endpoint_c('2').is_connected()
    assert root.endpoint_b('3').is_connected()
    assert root.endpoint_b('5').endpoint_d.is_connected()


def test__disconnect_root__all_endpoints_are_disconnected():
    root = EndpointRoot('base', '/')
    root.connect()
    root.disconnect()

    assert not root.is_connected()
    assert not root.endpoint_a.is_connected()
    assert not root.endpoint_a.endpoint_c.is_connected()
    assert not root.endpoint_b.is_connected()
    assert not root.endpoint_a('1').is_connected()
    assert not root.endpoint_a.endpoint_c('2').is_connected()
    assert not root.endpoint_b('3').is_connected()
