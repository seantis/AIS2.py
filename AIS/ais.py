# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""

import base64
import json
import uuid

import requests

from . import exceptions


from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .pdf import PDF


url = "https://ais.swisscom.com/AIS-Server/rs/v1.0/sign"


class AIS:
    """Client object holding connection information to the AIS service."""

    last_request_id: Optional[str]
    """Contains the id of the last request made to the AIS API."""

    def __init__(
        self,
        customer: str,
        key_static: str,
        cert_file: str,
        cert_key: str
    ):
        """Initialize an AIS client with authentication information."""
        self.customer = customer
        self.key_static = key_static
        self.cert_file = cert_file
        self.cert_key = cert_key

        self.last_request_id = None

    def _request_id(self) -> str:
        self.last_request_id = uuid.uuid4().hex
        return self.last_request_id

    def post(self, payload: str) -> Dict[str, Any]:
        """ Do the post request for this payload and return the signature part
        of the json response.
        """

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
        }
        cert = (self.cert_file, self.cert_key)
        response = requests.post(url, data=payload, headers=headers,
                                 cert=cert)
        sign_resp = response.json()['SignResponse']
        result = sign_resp['Result']
        if 'Error' in result['ResultMajor']:
            raise exceptions.error_for(response)
        return sign_resp

    def sign_batch(self, pdfs: Sequence['PDF']) -> None:
        """Sign a batch of files."""

        # Let's not be pedantic and allow a batch of size 1
        if len(pdfs) == 1:
            return self.sign_one_pdf(pdfs[0])

        payload_documents = {
            "DocumentHash": {
                "@ID": index,
                "dsig.DigestMethod": {
                    "@Algorithm":
                    "http://www.w3.org/2001/04/xmlenc#sha256"
                },
                "dsig.DigestValue": pdf.digest()
            }
            for index, pdf in enumerate(pdfs)
        }

        payload = {
            "SignRequest": {
                "@RequestID": self._request_id(),
                "@Profile": "http://ais.swisscom.ch/1.0",
                "OptionalInputs": {
                    "ClaimedIdentity": {
                        "Name": ':'.join((self.customer, self.key_static)),
                    },
                    "SignatureType": "urn:ietf:rfc:3369",
                    "AdditionalProfile":
                    "http://ais.swisscom.ch/1.0/profiles/batchprocessing",
                    "AddTimestamp": {"@Type": "urn:ietf:rfc:3161"},
                    "sc.AddRevocationInformation": {"@Type": "BOTH"},
                },
                "InputDocuments": payload_documents
            }
        }

        payload_json = json.dumps(payload, indent=4)
        sign_resp = self.post(payload_json)

        other = sign_resp['SignatureObject']['Other']['sc.SignatureObjects']
        for signature_object in other['sc.ExtendedSignatureObject']:
            signature = base64.b64decode(
                signature_object['Base64Signature']['$']
            )
            which_document = int(signature_object['@WhichDocument'])
            pdfs[which_document].write_signature(signature)

    def sign_one_pdf(self, pdf: 'PDF') -> None:
        """Sign the given pdf file."""

        payload = {
            "SignRequest": {
                "@RequestID": self._request_id(),
                "@Profile": "http://ais.swisscom.ch/1.0",
                "OptionalInputs": {
                    "ClaimedIdentity": {
                        "Name": ':'.join((self.customer, self.key_static)),
                    },
                    "SignatureType": "urn:ietf:rfc:3369",
                    "AddTimestamp": {"@Type": "urn:ietf:rfc:3161"},
                    "sc.AddRevocationInformation": {"@Type": "BOTH"},
                },
                "InputDocuments": {
                    "DocumentHash": {
                        "dsig.DigestMethod": {
                            "@Algorithm":
                            "http://www.w3.org/2001/04/xmlenc#sha256"
                        },
                        "dsig.DigestValue": pdf.digest()
                    },
                }
            }
        }

        sign_response = self.post(json.dumps(payload))
        signature = base64.b64decode(
            sign_response['SignatureObject']['Base64Signature']['$']
        )
        pdf.write_signature(signature)
