from unittest.mock import Mock

from boum.api_client.rest_client import Endpoint, RestClient


class TestEndpoint:
    class EndpointAC(Endpoint):
        def __init__(self, base_url: str, path: str):
            super().__init__(base_url, path)

    class EndpointA(Endpoint):
        def __init__(self, base_url: str, path: str):
            super().__init__(base_url, path)
            self.C = TestEndpoint.EndpointAC(self.url, "C")

    class EndpointB(Endpoint):
        def __init__(self, base_url: str, path: str):
            super().__init__(base_url, path)

    class EndpointRoot(Endpoint):
        def __init__(self, base_url: str, path: str):
            super().__init__(base_url, path)
            self.A = TestEndpoint.EndpointA(self.url, "A")
            self.B = TestEndpoint.EndpointB(self.url, "B")

    def test__create_root__urls_are_correct(self):
        root = TestEndpoint.EndpointRoot("base", "/")
        assert root.url == "base/"
        assert root.A.url == "base/A"
        assert root.A.C.url == "base/A/C"
        assert root.B.url == "base/B"

    def test__set_session__all_endpoints_have_session(self):
        root = TestEndpoint.EndpointRoot("base", "/")
        session = Mock()
        root.session = session

        assert root.session is session
        assert root.A.session is session
        assert root.A.C.session is session
        assert root.B.session is session


class TestRestClient:
    def test__enter__creates_session(self):
        root = Endpoint('base', '/')

        rest_client = RestClient(root)

        with rest_client:
            assert rest_client.endpoints.session is not None
