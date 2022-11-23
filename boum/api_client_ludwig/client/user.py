#!/usr/bin/env python
from boum.api_client_ludwig.utils import HttpMethods

class UserMixin:
    """Mixin including methods to call user related API endpoints.
    """

    def logout(self):
        """When logged in as a user, logs out from all accounts by deleting the refresh token.
        """
        # TODO: endpoint not yet implemented
        headers = self._get_default_headers_with_auth()
        url = "{}/logout".format(self._base_url)
        return self._handle_http_request(HttpMethods.POST, url, json={}, headers=headers)

    def get_user_details(self, user_id=None):
        """Calls the user endpoint to retrieve details about a user.

        Args:
            user_id (str): The id of the user for which to provide details (required if called
                by a pipeline or an admin user)

        Returns:
            ...
        """
        headers = self._get_default_headers_with_auth()
        url = "{}/user/{}".format(self._base_url, user_id)
        return self._handle_http_request(HttpMethods.GET, url, json={}, headers=headers).json()

    def create_user_account(self, email, password, account_type, **kwargs):
        """Calls the auth signup endpoint to create a new user account (coach or player).

        Args:
            email (str): E-mail of the user to be created.
            password (str): Password, of the user to be created.
        """
        headers = self._get_default_headers_with_auth()
        url = "{}/auth/signup".format(self._base_url)
        body = {
            "email": email,
            "password": password,
        }
        body.update(**kwargs)
        return self._handle_http_request(HttpMethods.POST, url, json=body, headers=headers).json()

