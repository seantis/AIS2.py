# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""
from common import fixture_path, BaseCase
from io import BytesIO

from AIS import PDF, SignatureTooLarge


class WeirdIO:
    def __init__(self, normal_io):
        self.io = normal_io

    def read(self, size=-1):
        return self.io.read(size)


class NonSeekableIO(WeirdIO):
    def seekable(self):
        return False


class TestPDF(BaseCase):

    def test_digest(self):
        pdf = PDF(fixture_path('one.pdf'))
        self.assertEqual(44, len(pdf.digest()))   # digest changes every time

    def test_write_signature(self):
        pdf = PDF(fixture_path('one.pdf'))
        pdf.digest()
        pdf.write_signature(b'0')
        assert pdf.out_stream is not None

    def test_write_signature_too_large(self):
        pdf = PDF(fixture_path('one.pdf'), sig_size=64)
        pdf.digest()
        with self.assertRaises(SignatureTooLarge, msg='84 bytes'):
            pdf.write_signature(b'0'*42)

    def test_write_signature_in_stream_in_place(self):
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = BytesIO(fp.read())

        pdf = PDF(in_stream=in_stream)
        pdf.digest()
        pdf.write_signature(b'0')
        assert pdf.out_stream is in_stream

    def test_write_signature_read_only_input(self):
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            pdf = PDF(fp)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is not fp

    def test_write_signature_weird_input(self):
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = WeirdIO(fp)
            pdf = PDF(in_stream)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is not in_stream

    def test_write_signature_non_seekable_input(self):
        with open(fixture_path('one.pdf'), mode='rb') as fp:
            in_stream = NonSeekableIO(fp)
            pdf = PDF(in_stream)
            pdf.digest()
            pdf.write_signature(b'0')
            assert pdf.out_stream is not in_stream
