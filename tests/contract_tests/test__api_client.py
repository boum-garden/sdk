from boum import constants
from boum.api_client_v1.v1.client import ApiClient


def test__signin_endpoint():
    client = ApiClient(constants.API_URL_LOCAL)

    with client:
        access_token, refresh_token = client.endpoints.auth.signin.post(
            'ludwig.auer@gmail.com', 'Test1234')

    assert access_token
    assert refresh_token


def test__refresh_token_endpoint():
    client = ApiClient(constants.API_URL_LOCAL)

    with client:
        access_token_1, refresh_token = client.endpoints.auth.signin.post(
            'ludwig.auer@gmail.com', 'Test1234')
        access_token_2 = client.endpoints.auth.token.post(refresh_token)

    assert access_token_2
    assert access_token_1 != access_token_2
