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
    INVALID_TOKEN_ERROR_MESSAGE = "InvalidToken"
    EXPIRED_TOKEN_ERROR_MESSAGE = "ExpiredToken"
    
