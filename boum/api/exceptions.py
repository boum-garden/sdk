from requests import HTTPError

class DownloadException(HTTPError):
    """Thrown when file could not be downloaded.
    """
    pass

class InvalidTokenException(HTTPError):
    """Thrown when JWT token is not valid.
    """
    pass

class MissingAverageCoordinatesException(HTTPError):
    """When average coordinates are missing in API response.
    """
    pass

class SessionExistsError(Exception):
    """Thrown when a session already exists
    """
    pass

class SessionOwnerError(Exception):
    """Thrown when a session is not owned
    by user requesting it.
    """
    pass

class UserRoleError(Exception):
    """Thrown when a user role issue occured.
    """
    pass

class InvalidParameterError(Exception):
    """Thrown when invalid parameters are passed to an
    API client method.
    """
    pass

class CreateContainerError(Exception):
    """Thrown when container creation fails
    """
    pass
