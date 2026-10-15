# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""
from __future__ import annotations

import pytest

from io import BytesIO
from tempfile import TemporaryFile

from AIS import PDF, SignatureTooLarge

from tests.common import fixture_path, BaseCase


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AIS.types import SupportsBinaryRead


class WeirdIO:
    def __init__(self, normal_io: SupportsBinaryRead) -> None:
        self.io = normal_io

    def read(self, size: int = -1) -> bytes:
        return self.io.read(size)


class NonSeekableIO(WeirdIO):
    def seekable(self) -> bool:
        return False


class TestPDF(BaseCase):

    def test_value_error_on_init(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Either input_file or in_stream'
        ):
            PDF(None)  # type: ignore

    def test_digest(self) -> None:
        pdf = PDF(fixture_path('one.pdf'))
        assert 44 == len(pdf.digest())   # digest changes every time

    def test_write_signature(self) -> None:
        pdf = PDF(fixture_path('one.pdf'))
        pdf.digest()
        pdf.write_signature(b'0')
        assert pdf.out_stream is not None

    def test_write_signature_too_large(self) -> None:
        pdf = PDF(fixture_path('one.pdf'), sig_size=64)
        pdf.digest()
        with pytest.raises(SignatureTooLarge, match=r'84 bytes'):
            pdf.write_signature(b'0'*42)

    def test_write_signature_inout_stream(self) -> None:
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = BytesIO(fp.read())

        pdf = PDF(inout_stream=in_stream)
        pdf.digest()
        pdf.write_signature(b'0')
        assert pdf.out_stream is in_stream

    def test_write_signature_out_stream(self) -> None:
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = BytesIO(fp.read())

        out_stream = BytesIO()
        pdf = PDF(in_stream, out_stream=out_stream)
        pdf.digest()
        pdf.write_signature(b'0')
        assert pdf.out_stream is out_stream
        assert in_stream.getvalue() != out_stream.getvalue()

    def test_write_signature_out_stream_file(self) -> None:
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = BytesIO(fp.read())

        with TemporaryFile() as out_stream:
            pdf = PDF(in_stream, out_stream=out_stream)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is out_stream
            out_stream.seek(0)
            assert in_stream.getvalue() != out_stream.read()

    def test_write_signature_read_only_input(self) -> None:
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            pdf = PDF(fp)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is not fp

    def test_write_signature_weird_input(self) -> None:
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = WeirdIO(fp)
            pdf = PDF(in_stream)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is not in_stream  # type: ignore[comparison-overlap]

    def test_write_signature_non_seekable_input(self) -> None:
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = NonSeekableIO(fp)
            pdf = PDF(in_stream)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is not in_stream  # type: ignore[comparison-overlap]
