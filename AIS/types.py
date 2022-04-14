# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""

from typing import Protocol
from typing import Union


class SupportsBinaryRead(Protocol):
    def read(self, __size: int = -1) -> bytes: ...


FileLike = Union[str, SupportsBinaryRead]
