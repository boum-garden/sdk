import functools
import logging
from abc import ABC, abstractmethod
from typing import Callable

import requests
from requests import JSONDecodeError


class Endpoint(ABC):
    """Baseclass for all endpoint clients.

    With this class you can create a tree hierarchy of endpoints that models the topology of a
    REST API.

    The subclasses of this class should implement the methods that correspond to the http verbs that
    the endpoint supports, using the provided private methods.

    if there are nested endpoints, the subclasses should also have attributes that represent the
    nested paths. These should also be subclasses of EndpointClient.

    Attributes
    ----------
        url : str
            The full url of the endpoint.
    """

    _session: requests.Session | None = None
    _headers: dict[str, str] = {}
    _refresh_access_token: Callable[[], None] = None
    _access_token_expired_message = 'AccessTokenExpired'  # nosec

    def __init__(
            self, path_segment: str, resource_id: str | None = None,
            disabled_for_collection: bool = False,
            refresh_access_token: Callable[[], None] = None,
            parent: 'Endpoint | None' = None):
        """
        Parameters
        ----------
            path_segment
                The path segment of the endpoint.
            resource_id
                The id of the resource that this endpoint represents. If it is none, the enpoint
                represents a collection of resources.
            parent
                The parent endpoint. If it is none, the endpoint is the root of the tree.
            refresh_access_token
                A callable that refreshes the access token.
            disabled_for_collection
                If true, the endpoint will not be accessible if no resource id is provided.
        """
        self._path_segment = path_segment
        Endpoint._refresh_access_token = refresh_access_token
        self._resource_id = resource_id
        self._disabled_for_collection = disabled_for_collection
        self._parent = parent

    @abstractmethod
    def __get__(self, instance, owner: type):
        """
        Validate attribute access and return a new instance of the attribute with a parent added.
        Every subclass must implement this method for propper type hinting with the propper
        return type as:
            def __get__(self, instance, owner: type) -> "...Endpoint":
                return super().__get__(instance, owner)
        """
        if isinstance(instance, Endpoint):
            if self._disabled_for_collection and instance.is_collection:
                raise AttributeError(
                    'This endpoint is only available for a single resource, not for a collection')
            return type(self)(
                path_segment=self._path_segment,
                resource_id=None,
                disabled_for_collection=self._disabled_for_collection,
                refresh_access_token=self._refresh_access_token,
                parent=instance)

        return self

    def __call__(self, resource_id: str):
        """
        Returns a new endpoint of the same classe with an added resource id, representing a
        specific resource instead of a collection.
        """
        return type(self)(
            path_segment=self._path_segment,
            resource_id=resource_id,
            disabled_for_collection=self._disabled_for_collection,
            refresh_access_token=self._refresh_access_token,
            parent=self._parent)

    @property
    def url(self) -> str:
        """The full url of the endpoint."""
        path_elemets = [self._parent.url if self._parent else None,
                        self._path_segment,
                        self._resource_id]
        return '/'.join(s.strip('/') for s in path_elemets if s)

    @property
    def is_collection(self) -> bool:
        """True if the endpoint represents a collection of resources."""
        return self._resource_id is None

    @property
    def is_resource(self) -> bool:
        """True if the endpoint represents a single resource."""
        return not self.is_collection

    @classmethod
    def set_session(cls, session: requests.Session):
        """Set the session for all Endpoint instances."""
        Endpoint._session = session

    # noinspection PyMethodParameters
    # pylint: disable=no-self-argument no-member protected-access
    def _request_handler(func: Callable[..., requests.Response]):
        """Decorator to apply the response handling method to the request methods"""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            def execute_and_parse():

                if not self._session:
                    raise RuntimeError('Endpoints are not connected to the API')

                response = func(self, *args, **kwargs)
                try:
                    message = response.json().get('message')
                except JSONDecodeError:
                    message = 'No message'
                return response, message

            logging.info("Calling %s on %s...", func.__name__, self.url)
            response, message = execute_and_parse()

            if response.status_code == 401 \
                    and self._access_token_expired_message == message:
                logging.info('Access token expired. Refreshing...')
                self._refresh_access_token()
                logging.info('Access token refreshed. Retrying request...')
                response, message = execute_and_parse()

            if response.ok:
                logging.info('Request successful (%s): %s', response.status_code, message)
            else:
                logging.error('Request failed (%s): %s', response.status_code, message)
                response.raise_for_status()

            return response

        return wrapper

    # noinspection PyArgumentList
    @_request_handler
    def _get(self, payload: dict = None, query_parameters: dict = None):
        """Send a GET request to the endpoint."""
        return self._session.get(url=self.url, json=payload, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _post(self, payload: dict = None, query_parameters: dict = None):
        """Send a POST request to the endpoint."""
        return self._session.post(url=self.url, json=payload, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _put(self, payload: dict = None, query_parameters: dict = None):
        """Send a PUT request to the endpoint."""
        return self._session.put(url=self.url, json=payload, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _patch(self, payload: dict = None, query_parameters: dict = None):
        """Send a PATCH request to the endpoint."""
        return self._session.patch(url=self.url, json=payload, params=query_parameters)

    # noinspection PyArgumentList
    @_request_handler
    def _delete(self, payload: dict = None, query_parameters: dict = None):
        """Send a DELETE request to the endpoint."""
        return self._session.delete(url=self.url, json=payload, params=query_parameters)
