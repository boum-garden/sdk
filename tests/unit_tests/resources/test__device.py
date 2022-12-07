from unittest.mock import Mock

import pytest

from boum.api_client.v1.client import ApiClient
from tests.fixtures.api import SignIn


@pytest.fixture
def session_mock():
    return Mock()


@pytest.fixture
def client(session_mock):
    session_mock.post.return_value = SignIn.response
    return ApiClient('email', 'password', base_url='base', session=session_mock)
