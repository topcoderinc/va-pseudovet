"""
the common errors defined and error_handler
"""

from http import HTTPStatus

from flask import jsonify
from werkzeug.exceptions import MethodNotAllowed, NotFound

from .logger import logger


class EntityNotFoundError(Exception):
    """
    backend will raise this error if entity not found
    """
    pass


class BadRequestError(Exception):
    """
    backend will raise this error if request params error or invoke params error
    """
    pass


class InnerServerError(Exception):
    """
    backend will raise this error if got some unexpected
    """
    pass


def error_handler(err):
    """
    handler errors and return message with http error code
    :param err: the error instance
    :return: the json response and error code
    """

    logger.error(type(err))
    logger.exception(err)

    err_type = type(err)
    error_message = str(err)
    error_code = HTTPStatus.INTERNAL_SERVER_ERROR

    if err_type is EntityNotFoundError or err_type is NotFound:
        error_code = HTTPStatus.NOT_FOUND
    elif err_type is BadRequestError:
        error_code = HTTPStatus.BAD_REQUEST
    elif err_type in (InnerServerError, TypeError):
        error_code = HTTPStatus.INTERNAL_SERVER_ERROR
    elif err_type is MethodNotAllowed:
        error_code = HTTPStatus.METHOD_NOT_ALLOWED
    return jsonify({'message': error_message}), error_code
