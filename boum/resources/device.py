from datetime import datetime, time

from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceState


class Device:
    """Abstration over the api client to easily interact with devices.

    Args:
        device_id (str): The device id
        api_client (ApiClient): The api client
    """

    def __init__(self, device_id: str, api_client: ApiClient):
        self.device_id = device_id
        self._api_client = api_client

    @staticmethod
    def get_device_ids(api_client: ApiClient) -> list[str]:
        """Get all device ids

        Args:
            api_client (ApiClient): The api client

        Returns:
            list[str]: The device ids
        """
        return api_client.endpoints.devices.get()

    def _set_desired_device_state(self, desired_device_state: DeviceState):
        self._api_client.endpoints.devices(self.device_id).patch(desired_device_state)

    def _get_reported_device_state(self) -> DeviceState:
        _, reported_device_state = self._api_client.endpoints.devices(self.device_id).get()
        return reported_device_state

    @property
    def pump_state(self) -> bool:
        """Get or set the pump state. ON = True, OFF = False (`bool`)
        """
        return self._get_reported_device_state().pump_state

    @pump_state.setter
    def pump_state(self, value: bool):
        desired_device_state = DeviceState(pump_state=value)
        self._set_desired_device_state(desired_device_state)

    @property
    def refill_time(self) -> list[time]:
        """Get or set the pump/refill times for a device (`list[time]`)
        """
        return self._get_reported_device_state().refill_time

    @refill_time.setter
    def refill_time(self, value: list[time]):
        desired_device_state = DeviceState(refill_time=value)
        self._set_desired_device_state(desired_device_state)

    def get_telemetry_data(self, start: datetime = None, end: datetime = None) -> dict[str, list]:
        """Get telemetry data for a device

        Args:
            start (datetime): The start date of the telemetry data
            end (datetime): The end date of the telemetry data

        Returns:
            dict[str, list]: The telemetry data
        """
        return self._api_client.endpoints.devices(self.device_id).data.get(start, end)
