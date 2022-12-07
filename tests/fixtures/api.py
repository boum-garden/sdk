from unittest.mock import Mock, call


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


class SignIn:
    call = signin = call(
        url='base/v1/auth/signin', json={'email': 'email', 'password': 'password'}, params=None)
    response = create_mock_response(
        200, data={'accessToken': 'acess_token', 'refreshToken': 'refresh_token'})


class TokenRefresh:
    call = call(
        url='base/v1/auth/token', json={'refreshToken': 'refresh_token'}, params=None)
    response = create_mock_response(200, data={'accessToken': 'acess_token'})


class DevicesGet:
    response = create_mock_response(200, data=[{'id': 'device_id'}])


class Shared:
    response_access_token_expired = create_mock_response(401, message='AccessTokenExpired')
