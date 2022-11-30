from datetime import datetime, time

from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models.device_state import DeviceState


class Device:
    # noinspection PyUnresolvedReferences
    """
        Abstration over the api client to easily interact with devices.

        Methods that get parts of the device state will return a tuple of the reported and desired
        state.

        Example
        -------
        >>> from datetime import time, datetime, timedelta
        >>> import pandas as pd
        >>> from boum.api_client.v1.client import ApiClient
        >>> from boum.resources.device import Device
        >>>
        >>> with ApiClient(email, password, base_url=base_url) as client:
        ...    # Get available device ids
        ...    device_ids = Device.get_device_ids(client)
        ...    # Create a device instance
        ...    device = Device(device_id, client)
        ...    # Remove device claim
        ...    device.unclaim()
        ...    # Claim a device
        ...    device.claim()
        ...    # Set the pump state
        ...    device.set_pump_state(True)  # True for on, False for off
        ...    # Get the pump state
        ...    reported, desired = device.get_pump_state()
        ...    # Set the refill time
        ...    device.set_refill_time(time(8, 0))
        ...    # Get the refill time
        ...    reported, desired = device.get_refill_time()
        ...    # Set the refill interval
        ...    device.set_refill_interval(3)
        ...    # Get the refill interval
        ...    reported, desired = device.get_refill_interval()
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

    def _get_device_states(self) -> (DeviceState, DeviceState):
        return self._api_client.root.devices(self.device_id).get()

    def get_pump_state(self) -> (bool, bool):
        """
        Get the pump state. Reported and desired values are returned as a tuple.

        Returns
        -------
            tuple[bool, bool]
        """
        reported, desired = self._get_device_states()
        return reported.pump_state, desired.pump_state

    def set_pump_state(self, value: bool):
        """
        Set the pump state.

        Parameters
        ----------
            value
                True for on, False for off
        """
        desired = DeviceState(pump_state=value)
        self._set_desired_device_state(desired)

    # noinspection PyTypeChecker
    def get_refill_time(self) -> (time, time):
        """
        Get the refill time. Reported and desired values are returned as a tuple.

        Returns
        -------
            tuple[time, time]
        """
        reported, desired = self._get_device_states()
        return reported.refill_time, desired.refill_time

    def set_refill_time(self, value: time):
        """
        Set the refill time.

        Parameters
        ----------
            value
                The time to refill the device
        """
        desired = DeviceState(refill_time=value)
        self._set_desired_device_state(desired)

    # noinspection PyTypeChecker
    def get_refill_interval(self) -> (int, int):
        """
        Get the refill interval. Reported and desired values are returned as a tuple.

        Returns
        -------
            tuple[int, int]
        """
        reported, desired = self._get_device_states()
        return reported.refill_interval, desired.refill_interval

    def set_refill_interval(self, days: int):
        """
        Set the refill interval.

        Parameters
        ----------
            days
                The number of days between refills
        """
        desired = DeviceState(refill_interval=days)
        self._set_desired_device_state(desired)

    def get_telemetry_data(self, start: datetime = None, end: datetime = None) -> dict[str, list]:
        """
        Get telemetry data for a device

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

    def claim(self, user_id: str = None):
        """
        Claim a device for the currently signed in use or a specified one.

        PArameters
        ----------
        user_id
            If this is specified, the device is claimed for the given user instead of the on that
            is signed in.
        """
        if user_id:
            self._api_client.root.devices.claim(user_id).put()
        else:
            self._api_client.root.devices.claim.put()

    def unclaim(self):
        """
        Remove any claim to the device.
        """
        self._api_client.root.devices.claim.delete()
