from boum import constants
from boum.api_client_v1.v1.client import ApiClient


def test_signin():

    client = ApiClient(constants.API_URL_LOCAL)

    with client:
        response = client.endpoints.auth.signin.post('ludwig.auer@gmail.com', 'Test1234')

