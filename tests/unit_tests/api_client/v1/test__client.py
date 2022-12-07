from unittest.mock import Mock

import pytest

from boum.api_client.v1.client import ApiClient
from tests.fixtures.api import SignIn, TokenRefresh, DevicesGet, Shared


@pytest.fixture
def session_mock():
    return Mock()


@pytest.fixture
def client(session_mock):
    session_mock.post.return_value = SignIn.response
    return ApiClient('email', 'password', base_url='base', session=session_mock)


def test__instantiated_with_email_and_password__signin_happens(client, session_mock):
    with client:
        assert session_mock.post.call_args_list == [SignIn.call]


def test__instantiated_with_refresh_token__only_token_refresh_happens(session_mock):
    session_mock.post.return_value = TokenRefresh.response
    client = ApiClient(refresh_token='refresh_token', base_url='base', session=session_mock)

    with client:
        assert session_mock.post.call_args_list == [TokenRefresh.call]


def test__if_previously_signed_in__nothing_happens(client, session_mock):
    with client:
        assert session_mock.post.call_args_list == [SignIn.call]

    with client:
        assert session_mock.post.call_args_list == [SignIn.call]


def test__if_access_token_expired__token_is_refreshed(client, session_mock):
    session_mock.get.side_effect = [Shared.response_access_token_expired, DevicesGet.response]
    session_mock.post.side_effect = [SignIn.response, TokenRefresh.response]

    with client:
        client.root.devices.get()
        assert session_mock.get.call_count == 2
        assert session_mock.post.call_args_list == [SignIn.call, TokenRefresh.call]
