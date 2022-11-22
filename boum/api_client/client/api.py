import os
import requests

from requests import HTTPError

from boum.api_client.exceptions import InvalidTokenException
from boum.api_client.utils import HttpMethods, HttpStatusCodes, ApiErrors
from boum.api_client.config import DefaultConfig

from .device import DeviceMixin
from .data import DataMixin
from .user import UserMixin

class Api(
        UserMixin,
        DeviceMixin,
        DataMixin
):
    """Api class
    """
    DEFAULT_HEADERS = {
        'Content-Type': "application/json"
    }

    TRIGGER_TOKEN_REFRESH = [
        ApiErrors.INVALID_TOKEN_ERROR_MESSAGE,
        ApiErrors.EXPIRED_TOKEN_ERROR_MESSAGE
    ]
    
    def __init__(self, email=None, password=None, refresh_token=None, base_url=None):

        # Not necessary, only for readability
        self._access_token = None
        self._refresh_token = None
        self._user_id = None

        if not base_url:
            if 'BOUM_API_BASE_URL' in os.environ:
                self._base_url = os.environ['BOUM_API_BASE_URL']
            else:
                self._base_url = DefaultConfig.BOUM_API_PROD_BASE_URL
        else:
            self._base_url = base_url

        if refresh_token:
            self.set_refresh_token(refresh_token)
        elif email and password:
            self.authenticate(email, password)
        elif 'BOUM_API_REFRESH_TOKEN' in os.environ:
            self._refresh_token = os.environ['BOUM_API_REFRESH_TOKEN']
        else:
            raise Exception(
                "Invalid arguments. No token or credentials provided. Token not found in process evn variable.")

        self._try_to_renew_access_token()

    def set_refresh_token(self, token):
        """This method sets refresh token process wide!

        NOTE: This  approach keeps the token in the env variable of the process. However
              every  other process run by the same user or root can still access it.  In
              case  of  unauthorized access to the machine running this code it would be
              slightly more secure to story only in memory. But is the machine access is
              compromised then leak of the refresh token is the least of a problem.

        Args:
            token: Refresh token that allows to obtains access tokens

        Returns:
            void

        """
        self._refresh_token = token

    def set_base_url(self, base_url):
        """Method to set the base url
        """
        self._base_url = base_url

    def get_base_url(self):
        """Method to get the base url
        """
        return self._base_url

    def get_refresh_token(self):
        """Method to get the refresh token
        """
        return self._refresh_token

    def authenticate(self, email, password):
        """Authorize as a user at the Boum API 

        Args:
            email(str): Email address to user for authorization
            password(str): Password under which to log in

        Returns: 
            void

        Raises:
            HttpException if auth fails
        """
        url = self._base_url + "/auth/login"
        params = {'email': email, 'password': password}
        result = self._handle_http_request(HttpMethods.POST, url, params=params)
        try:
            response = result.json()
            if result.ok and 'data' in response:
                if 'accessToken' in response['data'] \
                    and 'refreshToken' in response['data'] \
                        and 'userId' in response['data']:
                    self.set_refresh_token(response['refreshToken'])
                    self._set_access_token(response['accessToken'])
                    self._set_user_id(response['userId'])
            else:
                self._raise_http_error(
                    """Couldn't authenticate via email and password.
                    Credential incorrect or incomplete response from server.
                    Expected following fields: accessToken, refreshToken, userId.
                    Message: {}
                    """.format(response),HttpMethods.GET, url, result.status_code, params=params)
        except ValueError as error:
            self._raise_http_error("{}\n{}".format("Malformed response from auth endpoint", error.message),
                                    HttpMethods.GET, url, result.status_code, params=params)

    def _handle_http_request(self, method, url, **kwargs):
        """Wrapper function that handles http request and renews access token
        in case the API returns an InvalidTokenException.

        Args:
            method (str): "GET", "POST", "PATCH", "PUT", ...
            url (str): Base url of the REST API endpoint

        Returns:
            (:obj: `request.request`)
        """
        try:
            return self._perform_http_request(method, url, **kwargs)
        except InvalidTokenException:
            self._try_to_renew_access_token()
            headers = self._get_default_headers_with_auth()
            # update kwargs
            kwargs.update(dict(headers=headers))
            return self._perform_http_request(method, url, **kwargs)
                
    def _get_default_headers_with_auth(self):
        """Method returning the default authentification header.
        
        Returns:
            (:obj: `dict`): The auth header.
        """
        headers = {'Authorization': '{}'.format(self._access_token)}
        headers.update(self.DEFAULT_HEADERS)
        return headers

    def _perform_http_request(self, method, url, **kwargs):
        """Method that performs an HTTP request given a method and an url.

        Args:
            method (str): "GET", "POST", "PATCH", "PUT", ...
            url (str): Base url of the REST API endpoint

        Returns:
            (:obj: `request.request`)
        """
        req = requests.request(method, url, **kwargs)

        if req.status_code == HttpStatusCodes.INVALID_TOKEN:
            try:
                json = req.json()
                message = json.get('message')
                if message in self.TRIGGER_TOKEN_REFRESH:
                    raise InvalidTokenException(
                        "Provided token is invalid. Couldn't perform {} request for url: {} with args: {}"
                        .format(method, url, kwargs))
                else:
                    self._raise_http_error(json, method, url, req.status_code, **kwargs)
            except ValueError as error:
                self._raise_http_error("{}\n{}".format(req.text, error), method, url, req.status_code, **kwargs)
        elif not req.ok:
            self._raise_http_error(req.text, method, url, req.status_code, **kwargs)
        return req

    def _try_to_renew_access_token(self):
        """Method that creates a new accessToken using the refreshToken
        """
        url = self._base_url + "/auth/token"
        data = {'refreshToken': self._refresh_token}
        try:
            response = self._perform_http_request(HttpMethods.POST, url, json=data)
            self._set_access_token(response.json()['data']['accessToken'])
            return
        except InvalidTokenException as ex:
            self._raise_http_error(ex.message, HttpMethods.GET, url, None)

    def _set_access_token(self, token):
        """Method to set the access token variable
        """
        self._access_token = token

    def _set_user_id(self, user_id):
        """Method to set the user id variable
        """
        os.environ['USER_ID'] = user_id
        self._user_id = user_id

    def _raise_http_error(self, desc, method, url, status, **kwargs):
        """Method to raise a http error.

        TODO:
            * Is logging/throwing an exception with accessToken inside secure?
        """
        raise HTTPError(
            """
            Error while performing {} request for url: {} {}
            with args: {}
            {}
            """.format(method, url, "status code: {}".format(status) if status is not None else "", kwargs, desc))
