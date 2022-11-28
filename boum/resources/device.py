from datetime import datetime, time

from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceState


class Device:
    # noinspection PyUnresolvedReferences
    """
        Abstration over the api client to easily interact with devices.

        Example
        -------
        >>> from datetime import time, datetime, timedelta
        >>> import pandas as pd
        >>> from boum.api_client.v1.client import ApiClient
        >>> from boum.resources.device import Device
        >>>
        >>> with ApiClient(email, password, base_url) as client:
        ...    # Get available device ids
        ...    device_ids = Device.get_device_ids(client)
        ...    # Create a device instance
        ...    device = Device(device_ids[0], client)
        ...    # Set the pump state
        ...    device.pump_state = True  # True for on, False for off
        ...    # Set the refill times
        ...    device.refill_time = time(8, 0)
        ...    # Get the refill times
        ...    current_refill_times = device.refill_time
        ...    # Get device telemetry data
        ...    data = device.get_telemetry_data(start=datetime.now() - timedelta(days=1),
        ...        end=datetime.now())
        ...    # Convert telemetry data to pandas dataframe
        ...    df = pd.DataFrame(data)
        """

    def __init__(self, device_id: str, api_client: ApiClient):
        """
        Parameters
        ----------
            device_id
                The device id
            api_client
                The api client that handles the interaction with the api
        """
        self.device_id = device_id
        self._api_client = api_client

    @staticmethod
    def get_device_ids(api_client: ApiClient) -> list[str]:
        """Get all device ids

        Parameters
        ----------
            api_client
                The api client that handles the interaction with the api

        Returns
        -------
            list[str]
                The device ids
        """

        return api_client.root.devices.get()

    def _set_desired_device_state(self, desired_device_state: DeviceState):
        self._api_client.root.devices(self.device_id).patch(desired_device_state)

    def _get_reported_device_state(self) -> DeviceState:
        _, reported_device_state = self._api_client.root.devices(self.device_id).get()
        return reported_device_state

    @property
    def pump_state(self) -> bool:
        """Get or set the pump state. ON = True, OFF = False (`bool`)"""
        return self._get_reported_device_state().pump_state

    @pump_state.setter
    def pump_state(self, value: bool):
        desired_device_state = DeviceState(pump_state=value)
        self._set_desired_device_state(desired_device_state)

    # noinspection PyTypeChecker
    @property
    def refill_time(self) -> list[time]:
        """Get or set the pump/refill times for a device (`list[time]`)"""
        return self._get_reported_device_state().refill_time

    @refill_time.setter
    def refill_time(self, value: time):
        desired_device_state = DeviceState(refill_time=value)
        self._set_desired_device_state(desired_device_state)

    def get_telemetry_data(self, start: datetime = None, end: datetime = None) -> dict[str, list]:
        """Get telemetry data for a device

        Parameters
        ----------
            start
                The start date of the telemetry data
            end
                The end date of the telemetry data

        Returns
        -------
            dict[str, list]
                The telemetry data
        """

        return self._api_client.root.devices(self.device_id).data.get(start, end)
