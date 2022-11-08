#!/usr/bin/env python
from boum.api.utils import HttpMethods


class DeviceMixin:
    """Mixin including methods to call user related API endpoints.
    """

    def create_device(self):
        """Allows admins to create new boxes given a pre-defined serial number
        """
        headers = self._get_default_headers_with_auth()
        url = "{}/device/create".format(self._base_url)
        return self._handle_http_request(
            HttpMethods.POST, url, json=None, headers=headers
        ).json()

    def list_devices(self, user_id=None):
        """Allows admins to list all available devices in the DeviceRegistry
        collection and users to list all devices they own. When a user_id is
        provided and the endpoint is called by an admin, the devices owned by
        this user will be returned

        Args:
            user_id (str) [optional]: The userId of the user of whose devices should be listed.

        Returns:
            ...

        """
        # TODO implement user_id parameter in endpoint
        headers = self._get_default_headers_with_auth()
        url = "{}/device/list".format(self._base_url)
        return self._handle_http_request(
            HttpMethods.GET, url, json=None, headers=headers
        ).json()

    def get_device_details(self, device_id):
        """Allows admins and users to retrieve box details and history
        """
        headers = self._get_default_headers_with_auth()
        url = "{}/device/{}".format(device_id)
        return self._handle_http_request(
            HttpMethods.GET, url, json=None, headers=headers
        ).json()

    def claim_device(self, device_id, user_id=None):
        """Calls device endpoint to assign a device to a user. When called by an admin, the
        user_id needs to be provided

        Args:
            device_id (str): The id of the device which should be assigned to the user.
            user_id (str) [optional]: The userId of the user to which the device should be assigned.

        Returns:
            ...
        """

        # TODO, endpoint not implemented yet
        headers = self._get_default_headers_with_auth()
        url = "{}/device/claim?userId={}&deviceId={}".format(
            self._base_url, user_id, device_id
        )
        return self._handle_http_request(
            HttpMethods.PATCH, url, json=None, headers=headers
        )

    def update_device(self, device_id, payload):
        """Calls device endpoint to assign a device to a user. When called by an admin, the
        user_id needs to be provided

        Args:
            device_id (str): The id of the device which should be assigned to the user.
            user_id (str) [optional]: The userId of the user to which the device should be assigned.

        Returns:
            ...
        """

        # TODO, endpoint not implemented yet
        headers = self._get_default_headers_with_auth()
        url = "{}/device/{}".format(self._base_url, device_id)
        return self._handle_http_request(
            HttpMethods.PATCH, url, json=payload, headers=headers
        )


    def unclaim_device(self, device_id):
        """Calls device endpoint to unassign a device from a user. When called by a user
        only the devices owned by that user can be unclaimed.

        Args:
            box_id (str): The teamBoxId of the box which should be assigned to the user.

        Returns:
            ...
        """
        # TODO, endpoint not implemented yet
        headers = self._get_default_headers_with_auth()
        url = "{}/device/unclaim?deviceId={}".format(self._base_url, device_id)
        return self._handle_http_request(
            HttpMethods.PATCH, url, json=None, headers=headers
        )


    def start_pump(self, device_id):
        """Calls device endpoint to start the pump of a device
        """
        # TODO handle errors returned by API
        self.update_device(
            device_id, 
            {
                "state": {
                    "desired": {
                        "pumpState": "on"
                    }
                }
            }
        )

    def stop_pump(self, device_id):
        """Calls device endpoint to start the pump of a device
        """
        # TODO handle errors returned by API
        self.update_device(
            device_id, 
            {
                "state": {
                    "desired": {
                        "pumpState": "off"
                    }
                }
            }
        )

    def set_maximum_pump_duration(self, device_id, maximum_pump_duration='10min'):
        """Calls device endpoint to start the pump of a device
        """
        # TODO validation of maximum_pump_duration
        # TODO handle errors returned by API
        self.update_device(
            device_id, 
            {
                "state": {
                    "desired": {
                        "maximumPumpDuration": maximum_pump_duration
                    }
                }
            }
        )

    def set_maximum_pump_duration(self, device_id, refill_time='12:00'):
        """Calls device endpoint to start the pump of a device
        """
        # TODO validation of refill_time
        # TODO handle errors returned by API
        self.update_device(
            device_id, 
            {
                "state": {
                    "desired": {
                        "maximumPumpDuration": refill_time
                    }
                }
            }
        )

    def set_device_firmware(self, device_id, firmware_version='1.1.5'):
        """Calls device endpoint to start the pump of a device
        """
        # TODO validation of refill_time
        # TODO handle errors returned by API
        self.update_device(
            device_id, 
            {
                "state": {
                    "desired": {
                        "maximumPumpDuration": firmware_version
                    }
                }
            }
        )
