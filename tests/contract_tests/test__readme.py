from datetime import time, datetime

import pandas as pd

from boum.api_client import constants
from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceState
from boum.resources.device import Device

EMAIL = 'ludwig.auer@gmail.com'
PASSWORD = 'Test1234'


def test__api_client_instructions__work():
    with ApiClient(EMAIL, PASSWORD, constants.API_URL_LOCAL) as client:
        # Get call to the devices collection
        device_ids = client.root.devices.get()

        # Get call to a specific device
        device_states = client.root.devices(device_ids[0]).get()

        # Patch call to a specific device
        client.root.devices(device_ids[0]).patch(DeviceState())

        # Get call to a devices data
        data = client.root.devices(device_ids[0]).data.get()


def test__device_abstraction_instructions__work():
    with ApiClient(EMAIL, PASSWORD, constants.API_URL_LOCAL) as client:
        # Get available device ids
        device_ids = Device.get_device_ids(client)

        # Create a device instance
        device = Device(device_ids[0], client)

        # Set the pump state
        device.pump_state = True  # True for on, False for off

        # Set the refill times
        device.refill_time = time(8, 0)

        # Get the refill times
        current_refill_times = device.refill_time

        # Get device telemetry data
        data = device.get_telemetry_data(datetime.today(), datetime.now())

        # Convert telemetry data to pandas dataframe
        df = pd.DataFrame(data)
