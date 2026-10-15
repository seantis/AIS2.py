# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""
from __future__ import annotations

import json
import unittest

from os.path import dirname, join

from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from vcr import VCR  # type: ignore
from vcr.serializers import jsonserializer  # type: ignore


from typing import Any
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyhanko.sign.validation import PdfSignatureStatus

    from AIS import PDF


class JSONSerializer:
    """ Override default json serializer to fix PY3 vcr encoding mistake.
    """

    @staticmethod
    def fix_value_encoding(value: object) -> object:
        if isinstance(value, dict):
            return JSONSerializer.fix_dict_encoding(value)
        elif isinstance(value, list):
            return [JSONSerializer.fix_value_encoding(val) for val in value]
        elif isinstance(value, bytes):
            return value.decode('utf8')
        else:
            return value

    @staticmethod
    def fix_dict_encoding(dict_to_fix: dict[str, Any]) -> dict[str, Any]:
        """ Return a copy of *dict_to_fix* with bytes transform to str.

        :type dict_to_fix: dict
        :rtype: dict
        """
        return {
            key: JSONSerializer.fix_value_encoding(value)
            for key, value in dict_to_fix.items()
        }

    @staticmethod
    def serialize(cassette_dict: dict[str, Any]) -> str:
        cassette_dict = JSONSerializer.fix_dict_encoding(cassette_dict)
        return jsonserializer.serialize(cassette_dict)  # type: ignore[no-any-return]

    @staticmethod
    def deserialize(cassette_string: str) -> Any:
        return jsonserializer.deserialize(cassette_string)


def before_record_callback(request: Any) -> Any:
    """Replace confidential information in the recorded cassettes.

    - customer:key are replaced with 'X:Y'
    """
    body = request.body.decode('utf-8')

    payload = json.loads(body)
    payload['SignRequest']['OptionalInputs']['ClaimedIdentity']['Name'] = 'X:Y'
    request.body = json.dumps(payload)
    return request


my_vcr = VCR(
    serializer='json',
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'cassettes'),
    path_transformer=VCR.ensure_suffix('.json'),
    before_record=before_record_callback
)

my_vcr.register_serializer('json', JSONSerializer)


def fixture_path(filename: str) -> str:
    """Build the full path of a fixture file."""
    return join(dirname(__file__), 'fixtures', filename)


def validate_signature(pdf: PDF) -> PdfSignatureStatus:
    """Validate the pdf's signature"""
    # TODO: Add a ValidationContext to validate chain-of-trust?
    reader = PdfFileReader(pdf.out_stream)
    signature = reader.embedded_signatures[0]
    return validate_pdf_signature(signature)


class BaseCase(unittest.TestCase):
    pass
