# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from requests import Response


class AISError(Exception):
    """Generic AIS Error."""

    pass


class AuthenticationFailed(AISError):
    """Authentication with AIS failed.

    This means that AIS returned
    http://ais.swisscom.ch/1.0/resultminor/AuthenticationFailed
    """

    pass


class SignatureTooLarge(AISError):
    """The signature received from AIS is too large to store.

    This means the PDF needs to be created with a larger value
    for sig_size to store the signature.
    """

    def __init__(self, signature_size: int):
        self.signature_size = signature_size
        super().__init__(f'{signature_size} bytes')


class UnknownAISError(AISError):
    """Unknown AIS Error."""

    pass


minor_to_exception = {
    'http://ais.swisscom.ch/1.0/resultminor/AuthenticationFailed':
    AuthenticationFailed,
}


def error_for(response: 'Response') -> Exception:
    """Return the correct error for a response."""
    result = response.json()['SignResponse']['Result']

    Exc = minor_to_exception.get(result['ResultMinor'], UnknownAISError)
    return Exc(result)
