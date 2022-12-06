from unittest.mock import Mock, call

import pytest

from boum.api_client.v1.client import ApiClient


def create_mock_response(status_code, data=None, message: str | None = None):
    response = Mock()
    response.status_code = status_code
    if data or message:
        json = {}
        if data:
            json['data'] = data
        if message:
            json['message'] = message
        response.json.return_value = json
    return response


signin_response = create_mock_response(
    200, data={'accessToken': 'acess_token', 'refreshToken': 'refresh_token'})
token_refresh_response = create_mock_response(200, data={'accessToken': 'acess_token'})
access_token_expired_response = create_mock_response(401, message='AccessTokenExpired')
get_devices_response = create_mock_response(200, data=[{'id': 'device_id'}])

signin_call = call(
    url='base/v1/auth/signin', json={'email': 'email', 'password': 'password'}, params=None)
token_refresh_call = call(
    url='base/v1/auth/token', json={'refreshToken': 'refresh_token'}, params=None)


@pytest.fixture
def session_mock():
    return Mock()


@pytest.fixture
def client(session_mock):
    session_mock.post.return_value = signin_response
    return ApiClient('email', 'password', base_url='base', session=session_mock)


def test__instantiated_with_email_and_password__signin_happens(client, session_mock):
    with client:
        assert session_mock.post.call_args_list == [signin_call]


def test__instantiated_with_refresh_token__only_token_refresh_happens(session_mock):
    session_mock.post.return_value = token_refresh_response
    client = ApiClient(refresh_token='refresh_token', base_url='base', session=session_mock)

    with client:
        assert session_mock.post.call_args_list == [token_refresh_call]


def test__if_previously_signed_in__nothing_happens(client, session_mock):
    with client:
        assert session_mock.post.call_args_list == [signin_call]

    with client:
        assert session_mock.post.call_args_list == [signin_call]


def test__if_access_token_expired__token_is_refreshed(client, session_mock):
    session_mock.get.side_effect = [access_token_expired_response, get_devices_response]
    session_mock.post.side_effect = [signin_response, token_refresh_response]

    with client:
        client.root.devices.get()
        assert session_mock.get.call_count == 2
        assert session_mock.post.call_args_list == [signin_call, token_refresh_call]
