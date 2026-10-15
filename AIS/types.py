# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""
from __future__ import annotations

from typing import Protocol
from typing import TypeAlias


class SupportsBinaryRead(Protocol):
    def read(self, size: int = -1, /) -> bytes: ...


FileLike: TypeAlias = str | SupportsBinaryRead
