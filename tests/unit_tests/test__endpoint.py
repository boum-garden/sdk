from unittest.mock import Mock

from boum.api_client_v1.endpoint import EndpointClient


class EndpointClientAC(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)


class EndpointClientA(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.C = EndpointClientAC(self._url, 'C')


class EndpointClientB(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)


class EndpointClientRoot(EndpointClient):
    def __init__(self, base_url: str, path: str):
        super().__init__(base_url, path)
        self.A = EndpointClientA(self._url, 'A')
        self.B = EndpointClientB(self._url, 'B')


def test__no_resource_ids__urls_are_correct():
    root = EndpointClientRoot('base', '/')
    assert root.url == 'base/'
    assert root.A.url == 'base/A'
    assert root.A.C.url == 'base/A/C'
    assert root.B.url == 'base/B'


def test__with_resource_ids__urls_are_correct():
    root = EndpointClientRoot('base', '/')
    assert root.url == 'base/'
    assert root.A('1').url == 'base/A/1'
    assert root.A.C('2').url == 'base/A/C/2'
    assert root.A('3').C('4').url == 'base/A/3/C/4'
    assert root.B.url == 'base/B'


def test__set_session__all_endpoints_have_session():
    root = EndpointClientRoot('base', '/')
    session = Mock()
    root.session = session

    assert root.session is session
    assert root.A.session is session
    assert root.A.C.session is session
    assert root.B.session is session
