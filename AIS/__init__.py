# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""
from __future__ import annotations

from .ais import AIS
from .pdf import PDF
from .exceptions import (
    AISError,
    AuthenticationFailed,
    SignatureTooLarge,
    UnknownAISError,
)

__all__ = (
    'AIS',
    'PDF',
    'AISError',
    'AuthenticationFailed',
    'SignatureTooLarge',
    'UnknownAISError'
)

__version__ = '2.4.0'
