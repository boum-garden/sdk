from datetime import datetime, timedelta

from boum.api_client.v1.client import ApiClient
from boum.api_client.v1.models import DeviceStateModel, DeviceModel


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
        >>> from boum.api_client.v1.models import DeviceStateModel
        >>>
        >>> client = ApiClient(email, password, base_url=base_url)
        >>> # or ApiClient(refresh_token='token', base_url=base_url)
        >>>
        >>> with client:
        ...    # Get available device ids
        ...    device_ids = Device.get_device_ids(client)
        ...    # Create a device instance
        ...    device = Device(device_id, client)
        ...    # Remove device claim
        ...    # device.unclaim()
        ...    # Claim a device
        ...    # device.claim()
        ...    # Set desired device state
        ...    desired_device_State = DeviceStateModel(
        ...        pump_state=True,
        ...        refill_time=time(3, 32),
        ...        refill_interval_days=3,
        ...        max_pump_duration_minutes=5
        ...    )
        ...    device.set_desired_device_state(desired_device_State)
        ...    # Get reported and desired device state
        ...    reported, desired = device.get_device_states()
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

    @staticmethod
    def get_claimed_device_ids(api_client: ApiClient) -> list[str]:
        """Get all claimed device ids

        Parameters
        ----------
            api_client
                The api client that handles the interaction with the api

        Returns
        -------
            list[str]
                The device ids
        """
        return api_client.root.devices.claimed.get()
    
    @staticmethod
    def get_device_details(api_client: ApiClient, 
                           only_claimed: bool = False, 
                           only_tested: bool = False, 
                           sku_contains: str = '',
                           created_after: datetime = None) -> list[dict]:
        """Get details of all claimed devices

        Parameters
        ----------
            api_client
                The api client that handles the interaction with the api

        Returns
        -------
            list[dict]
                The device details
        """
        all_devices = api_client.root.devices.get(include_details=True)
        claimed_devices = api_client.root.devices.claimed.get(include_details=True)
        claimed_devices = {device['id']: device for device in claimed_devices}
        device_details_list = []
        for device in all_devices:
            add_device = True
            if only_claimed and device['id'] not in list(claimed_devices.keys()):
                add_device = False
            elif sku_contains and sku_contains not in device['sku']:
                add_device = False
            elif only_tested and 'hasBeenTested' in device:
                if not device['hasBeenTested']:
                    add_device = False
            elif created_after and datetime.fromtimestamp(device['createdAt']['_seconds']) < created_after:
                add_device = False
            if add_device:
                if only_claimed:
                    device['claimedAt'] = datetime.fromtimestamp(claimed_devices[device['id']]['createdAt']['_seconds'])
                    device['ownerId'] = claimed_devices[device['id']]['ownerId']
                device_details_list.append(device)
        return device_details_list
    
    def set_desired_device_state(self, desired_device_state: DeviceStateModel):
        """
        Set the desired device state.

        Parameters
        ----------
            desired_device_state
                The desired device state
        """
        device_model = DeviceModel(desired_device_state)
        self._api_client.root.devices(self.device_id).patch(device_model)

    def get_device_states(self) -> (DeviceStateModel, DeviceStateModel):
        """
        Get the reported and desired device state.

        Returns
        -------
            a tuple with the reported and desired device states
        """
        device_model = self._api_client.root.devices(self.device_id).get()
        return device_model.reported_state, device_model.desired_state

    def get_telemetry_data(
            self, start: datetime = None, end: datetime = None,
            interval: timedelta = None) -> dict[str, list]:
        """
        Get telemetry data for a device

        Parameters
        ----------
            start
                The start date of the telemetry data
            end
                The end date of the telemetry data
            interval
                the interpolation interavl for the telemetry data

        Returns
        -------
            dict[str, list]
                The telemetry data in a format that can be easily converted to a pandas dataframe.
        """
        device_data_model = self._api_client.root.devices(self.device_id).data.get(
            start, end, interval)
        return device_data_model.data

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
            self._api_client.root.devices(self.device_id).claim(user_id).put()
        else:
            self._api_client.root.devices(self.device_id).claim.put()

    def unclaim(self):
        """
        Remove any claim to the device.
        """
        self._api_client.root.devices(self.device_id).claim.delete()
