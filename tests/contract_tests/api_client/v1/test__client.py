import pytest
from requests import HTTPError

from boum import constants
from boum.api_client.v1.client import ApiClient

EMAIL = 'ludwig.auer@gmail.com'
PASSWORD = 'Test1234'


@pytest.fixture
def client():


    return ApiClient(constants.API_URL_LOCAL)


def test__auth_flow__works(client):
    with client:
        client.signin(EMAIL, PASSWORD)
        client.refresh_access_token()


def test__signin_with_bad_credentials__raises_http_error(client):
    with client:
        with pytest.raises(HTTPError):
            client.signin(EMAIL, 'bad_password')


def test__refresh_access_token_without_token__raises_attribute_error(client):
    with client:
        with pytest.raises(AttributeError):
            client.refresh_access_token()
