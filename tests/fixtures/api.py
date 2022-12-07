"""
This module provides
- mock responses for the session object of the ApiClient and Endpoint classes.
- call objects with the correct attributes for the request methods of the session objects.

IMPORTANT: If these objects don't match the the expected requests and responses that the API
can process, the unit test will not test the code in the correct way. Therefore this module has
kept up-to-date with the API
"""
from datetime import time, datetime, timedelta
from unittest.mock import Mock, call

from boum.api_client.v1.models import DeviceStateModel

DEVICE_ID = 'device_id'
EMAIL = 'email'
PASSWORD = 'password'
BASE_URL = 'base'
REFRESH_TOKEN = 'refresh_token'
ACCESS_TOKEN = 'access_token'
USER_ID = 'user_id'


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


class AuthSigningPost:
    call = signin = call(
        url=f'{BASE_URL}/v1/auth/signin', json={'email': EMAIL, 'password': PASSWORD}, params=None)
    response = create_mock_response(
        200, data={'accessToken': ACCESS_TOKEN, 'refreshToken': REFRESH_TOKEN})


class AuthTokenPost:
    call = call(
        url=f'{BASE_URL}/v1/auth/token', json={'refreshToken': REFRESH_TOKEN}, params=None)
    response = create_mock_response(200, data={'accessToken': ACCESS_TOKEN})


class DevicesGet:
    response = create_mock_response(200, data=[{'id': DEVICE_ID}])
    call = call(url=f'{BASE_URL}/v1/devices', json=None, params=None)


class DevicesWithIdGet:
    desired_state = DeviceStateModel(
        pump_state=True,
        refill_time=time(3, 45),
        refill_interval_days=1,
        max_pump_duration_minutes=2,
    )
    reported_state = DeviceStateModel(
        pump_state=False,
        refill_time=time(1, 23),
        refill_interval_days=4,
        max_pump_duration_minutes=5
    )
    response = create_mock_response(
        200, data={
            'desired': {
                'pumpState': 'on', 'refillTime': '03:45', 'refillInterval': '1days',
                'maxPumpDuration': '2min'
            },
            'reported': {
                'pumpState': 'off', 'refillTime': '01:23', 'refillInterval': '4days',
                'maxPumpDuration': '5min'
            }
        })
    call = call(url=f'{BASE_URL}/v1/devices/{DEVICE_ID}', json=None, params=None)


class DevicesWithIdPatch:
    desired_state = DeviceStateModel(
        pump_state=True,
        refill_time=time(3, 45),
        refill_interval_days=1,
        max_pump_duration_minutes=2,
    )
    response = create_mock_response(200)
    call = call(
        url=f'{BASE_URL}/v1/devices/{DEVICE_ID}',
        json={
            'state': {
                'desired': {
                    'pumpState': 'on', 'refillTime': '03:45', 'refillInterval': '1days',
                    'maxPumpDuration': '2min'
                }
            }
        },
        params=None)


class DevicesWithIdClaimPut:
    response = create_mock_response(200, data={})
    call = call(url=f'{BASE_URL}/v1/devices/{DEVICE_ID}/claim', json=None, params=None)


class DevicesWithIdClaimWithIdPut:
    response = create_mock_response(200, data={})
    call = call(url=f'{BASE_URL}/v1/devices/{DEVICE_ID}/claim/{USER_ID}', json=None, params=None)


class DevicesWithIdClaimDelete:
    response = create_mock_response(200, data={})
    call = call(url=f'{BASE_URL}/v1/devices/{DEVICE_ID}/claim', json=None, params=None)


class DevicesWithIdDataGet:
    start = datetime(2022, 1, 2, 3, 4, 5)
    end = datetime(2023, 6, 7, 8, 9, 10)
    interval = timedelta(minutes=11)
    data_clean = expected = {
        'deviceId': [DEVICE_ID, DEVICE_ID],
        'timestamp': ['2022-01-02T03:04:05Z', '2023-06-07T08:09:10Z'],
        'someValue': [1, 2]
    }
    response = create_mock_response(
        200, data={
            'details': {
                'deviceId': DEVICE_ID
            },
            'timeSeries': {
                'someValue': [
                    {'x': '2022-01-02T03:04:05Z', 'y': 1},
                    {'x': '2023-06-07T08:09:10Z', 'y': 2}
                ]
            }
        })
    call_no_args = call(url=f'{BASE_URL}/v1/devices/{DEVICE_ID}/data', json=None, params={})
    call_time_limit_args = call(
        url=f'{BASE_URL}/v1/devices/{DEVICE_ID}/data', json=None,
        params={'timeStart': '2022-01-02T03:04:05Z', 'timeEnd': '2023-06-07T08:09:10Z'})
    call_interval_args = call(
        url=f'{BASE_URL}/v1/devices/{DEVICE_ID}/data', json=None,
        params={'interval': '11m'})


class Shared:
    response_access_token_expired = create_mock_response(401, message='AccessTokenExpired')
