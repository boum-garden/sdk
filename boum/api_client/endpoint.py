import functools
from typing import Callable

import requests


class EndpointClient:
    _session: requests.Session | None = None
    _headers: dict[str, str] = {}

    def __init__(
            self, base_url: str, path: str, parent: "EndpointClient | None",
            resource_id: str | None = None):
        self._base_url = base_url
        self._path = path
        self.resource_id = resource_id
        self.url = '/'.join(s.strip('/') for s in [base_url, path, resource_id] if s)
        self._parent = parent

    def __call__(self, resource_id: str):
        return type(self)(self._base_url, self._path, self._parent, resource_id)

    @classmethod
    def connect(cls):
        EndpointClient._session = requests.Session()
        EndpointClient._session.headers = cls._headers

    @classmethod
    def disconnect(cls):
        EndpointClient._session.close()
        EndpointClient._session = None

    @classmethod
    def is_connected(cls):
        return cls._session is not None

    @classmethod
    def set_access_token(cls, access_token: str):
        auth_header = {'Authorization': f'{access_token}'}
        EndpointClient._headers.update(auth_header)

    @staticmethod
    def handle_response(func: Callable[..., requests.Response]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response

        return wrapper

    @handle_response
    def _get(self, query_parameters: dict = None):
        return self._session.get(url=self.url, params=query_parameters)

    @handle_response
    def _post(self, payload: dict = None, query_parameters: dict = None):
        return self._session.post(url=self.url, json=payload, params=query_parameters)

    @handle_response
    def _patch(self, payload: dict = None, query_parameters: dict = None):
        return self._session.patch(url=self.url, json=payload, params=query_parameters)

    @handle_response
    def _delete(self, query_parameters: dict = None):
        return self._session.delete(url=self.url, params=query_parameters)
