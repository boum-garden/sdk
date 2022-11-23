import requests as requests


class Endpoint:
    def __init__(self, base_url: str, path: str):
        self.url = '/'.join(s.strip('/') for s in [base_url, path])
        self._session: requests.Session | None = None

    @property
    def endpoints(self) -> list["Endpoint"]:
        return [v for v in vars(self).values() if issubclass(type(v), Endpoint)]

    @property
    def session(self) -> requests.Session:
        return self._session

    @session.setter
    def session(self, session: requests.Session):
        self._session = session
        for endpoint in self.endpoints:
            endpoint.session = session


class RestClient:
    def __init__(self, root: Endpoint):
        self.endpoints = root
        self._session: None | requests.Session = None

    def __enter__(self) -> "RestClient":
        self._session = requests.Session()
        self.endpoints.session = self._session
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
