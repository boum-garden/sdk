import pytest

from boum.api_client.v1.client import ApiClient

# pylint: disable=unused-variable
def test__multiple_instances__raise_error():

    client_1 = ApiClient('email', 'password')

    with pytest.raises(AttributeError):
        client_2 = ApiClient('email', 'password')
