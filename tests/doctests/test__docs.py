import doctest

import boum.api_client.v1.client
import boum.resources.device
from tests.fixtures.env import EMAIL, PASSWORD, DEVICE_ID, BASE_URL

execution_context = {
    'email': EMAIL,
    'password': PASSWORD,
    'device_id': DEVICE_ID,
    'base_url': BASE_URL
}


def test__readme():
    doctest.testfile('../../README.md', raise_on_error=True, verbose=True, globs=execution_context)


def test__client():
    doctest.testmod(
        boum.api_client.v1.client, raise_on_error=True, verbose=True, globs=execution_context)


def test__device():
    doctest.testmod(
        boum.resources.device, raise_on_error=True, verbose=True, globs=execution_context)
