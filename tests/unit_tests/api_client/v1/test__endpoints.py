from boum.api_client.v1.endpoints import EndpointClient


class EndpointClientAC(EndpointClient):
    pass


class EndpointClientA(EndpointClient):
    def __init__(
            self, base_url: str, path: str, parent: EndpointClient, resource_id: str | None = None):
        super().__init__(base_url, path, parent, resource_id)
        self.endpoint_c = EndpointClientAC(self.url, 'C', self)


class EndpointClientB(EndpointClient):
    pass


class EndpointClientRoot(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path, None)
        self.endpoint_a = EndpointClientA(self.url, 'A', self)
        self.endpoint_b = EndpointClientB(self.url, 'B', self)


def test__create__urls_are_correct():
    root = EndpointClientRoot('base', '/')
    assert root.url == 'base/'
    assert root.endpoint_a.url == 'base/A'
    assert root.endpoint_a.endpoint_c.url == 'base/A/C'
    assert root.endpoint_b.url == 'base/B'
    assert root.endpoint_a('1').url == 'base/A/1'
    assert root.endpoint_a.endpoint_c('2').url == 'base/A/C/2'
    assert root.endpoint_a('3').endpoint_c('4').url == 'base/A/3/C/4'


def test__connect_root__all_endpoints_are_connected():
    root = EndpointClientRoot('base', '/')
    root.connect()

    assert root.is_connected()
    assert root.endpoint_a.is_connected()
    assert root.endpoint_a.endpoint_c.is_connected()
    assert root.endpoint_b.is_connected()
    assert root.endpoint_a('1').is_connected()
    assert root.endpoint_a.endpoint_c('2').is_connected()
    assert root.endpoint_b('3').is_connected()


def test__disconnect_root__all_endpoints_are_disconnected():
    root = EndpointClientRoot('base', '/')
    root.connect()
    root.disconnect()

    assert not root.is_connected()
    assert not root.endpoint_a.is_connected()
    assert not root.endpoint_a.endpoint_c.is_connected()
    assert not root.endpoint_b.is_connected()
    assert not root.endpoint_a('1').is_connected()
    assert not root.endpoint_a.endpoint_c('2').is_connected()
    assert not root.endpoint_b('3').is_connected()
