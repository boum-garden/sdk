from boum.api_client.endpoint import EndpointClient


class EndpointClientAC(EndpointClient):
    pass


class EndpointClientA(EndpointClient):
    def __init__(
            self, base_url: str, path: str, parent: EndpointClient, resource_id: str | None = None):
        super().__init__(base_url, path, parent, resource_id)
        self.c = EndpointClientAC(self.url, 'C', self)


class EndpointClientB(EndpointClient):
    pass


class EndpointClientRoot(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path, None)
        self.a = EndpointClientA(self.url, 'A', self)
        self.b = EndpointClientB(self.url, 'B', self)


def test__create__urls_are_correct():
    root = EndpointClientRoot('base', '/')
    assert root.url == 'base/'
    assert root.a.url == 'base/A'
    assert root.a.c.url == 'base/A/C'
    assert root.b.url == 'base/B'
    assert root.a('1').url == 'base/A/1'
    assert root.a.c('2').url == 'base/A/C/2'
    assert root.a('3').c('4').url == 'base/A/3/C/4'


def test__connect_root__all_endpoints_are_connected():
    root = EndpointClientRoot('base', '/')
    root.connect()

    assert root.is_connected()
    assert root.a.is_connected()
    assert root.a.c.is_connected()
    assert root.b.is_connected()
    assert root.a('1').is_connected()
    assert root.a.c('2').is_connected()
    assert root.b('3').is_connected()


def test__disconnect_root__all_endpoints_are_disconnected():
    root = EndpointClientRoot('base', '/')
    root.connect()
    root.disconnect()

    assert not root.is_connected()
    assert not root.a.is_connected()
    assert not root.a.c.is_connected()
    assert not root.b.is_connected()
    assert not root.a('1').is_connected()
    assert not root.a.c('2').is_connected()
    assert not root.b('3').is_connected()
