import random
from datetime import datetime, timedelta, time

import pytest
from requests import HTTPError

from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceModel, DeviceStateModel, UserModel, DeviceDataModel
from tests.fixtures.env import EMAIL, PASSWORD, DEVICE_ID, USER_ID, BASE_URL


@pytest.fixture(scope='module')
def client():
    with ApiClient(EMAIL, PASSWORD, base_url=BASE_URL) as client:
        yield client


class TestApiClient:

    def test__instantiate_with_refresh_token__works(self, client):
        _, refresh_token = client.root.auth.signin.post(EMAIL, PASSWORD)

        with ApiClient(refresh_token=refresh_token, base_url=BASE_URL):
            pass


class TestAuthSigninEndpoint:

    def test__post__works(self, client):
        access_token, refresh_token = client.root.auth.signin.post(EMAIL, PASSWORD)

        assert access_token
        assert refresh_token


class TestAuthTokenEndpoint:

    def test__post__works(self, client):
        access_token_1, refresh_token = client.root.auth.signin.post(EMAIL, PASSWORD)
        access_token_2 = client.root.auth.token.post(refresh_token)

        assert access_token_2
        assert access_token_1 != access_token_2


class TestDevicesEndpoint:

    @pytest.fixture
    def device_model(self):
        return DeviceModel(desired_state=DeviceStateModel())

    @pytest.mark.flaky(reruns=3)
    def test__get_without_device_id__returns_list_with_device_id(self, client):
        result = client.root.devices.get()
        assert result == [DEVICE_ID]

    @pytest.mark.flaky(reruns=10)
    @pytest.mark.parametrize('pump_state', [True, False])
    def test__patch_and_get_with_device_id__sets_and_returns_new_desired_state(
            self, client, pump_state: bool):
        desired_state_in = DeviceStateModel(
            pump_state=pump_state,
            refill_time=time(random.randint(0, 23), random.randint(0, 59)),
            refill_interval_days=random.randint(1, 10),
            max_pump_duration_minutes=random.randint(0, 10),
        )
        device_model_in = DeviceModel(desired_state_in)

        client.root.devices(DEVICE_ID).patch(device_model_in)
        device_model_out = client.root.devices(DEVICE_ID).get()

        assert device_model_out.desired_state == desired_state_in
        assert isinstance(device_model_out.reported_state, DeviceStateModel)
        assert device_model_out.reported_state

    def test__post_without_device_id__raises_401_error(self, client):
        with pytest.raises(HTTPError) as e:
            client.root.devices.post()
            assert e.value.response.status_code == 401


class TestDevicesDataEndpoint:

    @pytest.mark.flaky(reruns=3)
    def test__get_without_arguments__returns_data(self, client):
        result = client.root.devices(DEVICE_ID).data.get()
        assert isinstance(result, DeviceDataModel)

    @pytest.mark.flaky(reruns=3)
    def test__get_with_time_restrictions__returns_data(self, client):
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        interval = timedelta(minutes=1)
        result = client.root.devices(DEVICE_ID).data.get(start=start, end=end, interval=interval)
        assert isinstance(result, DeviceDataModel)


class TestDevicesClaimEndpoint:

    @pytest.mark.flaky(reruns=3)
    def test__put_with_user_id__works(self, client):
        try:
            client.root.devices(DEVICE_ID).claim.delete()
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e
        client.root.devices(DEVICE_ID).claim.put()

    @pytest.mark.flaky(reruns=3)
    def test__delete_and_put_without_user_id__works(self, client):
        try:
            client.root.devices(DEVICE_ID).claim.put()
        except HTTPError as e:
            if e.response.status_code != 401:
                raise e
        client.root.devices(DEVICE_ID).claim.delete()
        client.root.devices(DEVICE_ID).claim.put()


class TestUsersEndpoint:

    def test__get_without_user_id__works(self, client):
        result = client.root.users.get()
        assert isinstance(result, UserModel)

    def test__get_with_user_id__works(self, client):
        result = client.root.users(USER_ID).get()
        assert isinstance(result, UserModel)

    def test__get_with_wrong_user_id__raises_http_error(self, client):
        with pytest.raises(HTTPError):
            client.root.users('some_user_id').get()
