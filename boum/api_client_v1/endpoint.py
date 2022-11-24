import functools
from typing import Callable

import requests as requests


class EndpointClient:
    _session: requests.Session | None

    def __init__(self, base_url: str, path: str):
        self._url = '/'.join(s.strip('/') for s in [base_url, path])
        self._resource_id: str | None = None

    def __call__(self, resource_id: str):
        # TODO: check that resource id is valid
        self._resource_id = resource_id
        return self

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session: requests.Session):
        EndpointClient._session = session

    @property
    def url(self):
        return self._url if not self._resource_id else '/'.join([self._url, self._resource_id])

    @property
    def endpoints(self) -> list["EndpointClient"]:
        return [v for v in vars(self).values() if issubclass(type(v), EndpointClient)]

    @staticmethod
    def handle_response(func: Callable[..., requests.Response]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response

        return wrapper

    @handle_response
    def _get(self):
        return self.session.get(url=self._url)

    @handle_response
    def _post(self, payload: dict = None):
        return self.session.post(url=self._url, json=payload)

    @handle_response
    def _patch(self, payload: dict = None):
        return self.session.patch(url=self._url, json=payload)

    @handle_response
    def _delete(self):
        return self.session.delete(url=self._url)
