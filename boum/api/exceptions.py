from requests import HTTPError


class InvalidTokenException(HTTPError):
    """Thrown when JWT token is not valid.
    """
    pass