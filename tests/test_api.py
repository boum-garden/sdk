import os
import pytest

from boum.api.client.api import Api
from boum.api.config import DefaultConfig
from boum.api.utils import HttpStatusCodes

@pytest.yield_fixture(scope="function")
def api_fixture():
    email = "ludwig.auer@gmail.com"
    password = "Test1234"

    api_user = Api(
        email=email, password=password,
        base_url=DefaultConfig.BOUM_API_PROD_BASE_URL
    )
    api_admin = Api(
        token=os.environ['BOUM_API_PROD_REFRESH_TOKEN'],
        base_url=DefaultConfig.BOUM_API_PROD_BASE_URL
    )

    yield api_user, api_admin

def test_update_device(api_fixture):
    """Tests whether changing session processing statuses works.
    """
    device_id = '...'

    api_user = api_fixture[0]
    api_admin = api_fixture[1]

    response = api_admin.start_pump(device_id)
    assert response.status_code is HttpStatusCodes.SUCCESS_EMPTY

    response = api_admin.stop_pump(device_id)
    assert response.status_code is HttpStatusCodes.SUCCESS_EMPTY

    response = api_admin.set_refill_time(device_id)
    assert response.status_code is HttpStatusCodes.SUCCESS_EMPTY

    response = api_admin.set_maximum_pump_duration(device_id)
    assert response.status_code is HttpStatusCodes.SUCCESS_EMPTY
