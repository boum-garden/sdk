#!/usr/bin/env python

class HttpMethods:
    """Config class that collects all HTTP methods.
    """
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'

class HttpStatusCodes:
    """Config class that collects all HTTP status codes.
    """
    INVALID_TOKEN = 401
    SUCCESS_EMPTY = 204
    NOT_FOUND = 404
    SUCCESS = 200
    
class ApiErrors:
    """Config class that collects all API error codes.
    """
    INVALID_TOKEN_ERROR_MESSAGE = "Auth_InvalidToken"
    EXPIRED_TOKEN_ERROR_MESSAGE = "Auth_ExpiredToken"

class UserRoleCodes:
    """Config class that collects all user roles.
    """
    ADMIN = 1000
    PIPELINE = 900
    COACH = 200
    PLAYER = 100

class UserRoleNames:
    """Config class that collects all user roles.
    """
    ADMIN = "admin"
    PIPELINE = "pipeline"
    COACH = "coach"
    PLAYER = "player"

class SessionStatus:
    """Config class collecting relevant session statuses.

    Note: Session statuses are stored in our PostgreSQL database
        and used to communicate the processing status to the user.

    """
    ANALYSING = 10100
    UPLOADED = 10000
    COMPLETED = 4
    FAILED = 10
    PENDING = 5100
    EXCLUDED = 99 # deprecated, we are using a flag isExcluded now
    
