"""
This module tests the api client up to the calls to the API with the session
object. It relies on the API fixtures and on their correct representation of the actual API.
"""

from unittest.mock import Mock

import pytest

from boum.api_client.v1.client import ApiClient
from tests.fixtures.api import AuthSigningPost, AuthTokenPost, DevicesGet, Shared, EMAIL, \
    PASSWORD, BASE_URL, REFRESH_TOKEN


@pytest.fixture
def session_mock():
    return Mock()


@pytest.fixture
def client(session_mock):
    session_mock.post.return_value = AuthSigningPost.response
    return ApiClient(EMAIL, PASSWORD, base_url=BASE_URL, session=session_mock)


class TestAuthLogic:
    def test__instantiated_with_email_and_password__signin_happens(self, client, session_mock):
        with client:
            assert session_mock.post.call_args == AuthSigningPost.call

    def test__instantiated_with_refresh_token__only_token_refresh_happens(self, session_mock):
        session_mock.post.return_value = AuthTokenPost.response
        client = ApiClient(refresh_token=REFRESH_TOKEN, base_url=BASE_URL, session=session_mock)

        with client:
            assert session_mock.post.call_args == AuthTokenPost.call

    def test__if_previously_signed_in__nothing_happens(self, client, session_mock):
        with client:
            assert session_mock.post.call_args == AuthSigningPost.call

        with client:
            assert session_mock.post.call_args == AuthSigningPost.call

    def test__if_access_token_expired__token_is_refreshed(self, client, session_mock):
        session_mock.get.side_effect = [Shared.response_access_token_expired, DevicesGet.response]
        session_mock.post.side_effect = [AuthSigningPost.response, AuthTokenPost.response]

        with client:
            client.root.devices.get()
            assert session_mock.get.call_count == 2
            assert session_mock.post.call_args_list == [AuthSigningPost.call, AuthTokenPost.call]
