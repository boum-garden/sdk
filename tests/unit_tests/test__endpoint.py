from unittest.mock import Mock

from boum.api_client_v1.endpoint import EndpointClient


class EndpointClientAC(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)


class EndpointClientA(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.c = EndpointClientAC(self._url, 'C')


class EndpointClientB(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)


class EndpointClientRoot(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.a = EndpointClientA(self._url, 'A')
        self.b = EndpointClientB(self._url, 'B')


def test__create__urls_are_correct():
    root = EndpointClientRoot('base', '/')
    assert root.url == 'base/'
    assert root.a.url == 'base/A'
    assert root.a.c.url == 'base/A/C'
    assert root.b.url == 'base/B'
    assert root.a('1').url == 'base/A/1'
    assert root.a.c('2').url == 'base/A/C/2'
    assert root.a('3').c('4').url == 'base/A/3/C/4'


def test__set_session__all_endpoints_have_session():
    root = EndpointClientRoot('base', '/')
    session = Mock()
    root.session = session

    assert root.session is session
    assert root.a.session is session
    assert root.a.c.session is session
    assert root.b.session is session
    assert root.a('1').session is session
    assert root.a.c('2').session is session
    assert root.b('3').session is session
