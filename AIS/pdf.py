# -*- coding: utf-8 -*-
"""
AIS.py - A Python interface for the Swisscom All-in Signing Service.

:copyright: (c) 2016 by Camptocamp
:license: AGPLv3, see README and LICENSE for more details

"""

import base64
from datetime import datetime
import io

from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields
from pyhanko.sign import signers
from pyhanko.sign.signers import cms_embedder

from .exceptions import SignatureTooLarge


from typing import overload
from typing import BinaryIO
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .types import FileLike
    from .types import SupportsBinaryRead


def is_seekable(fp: 'SupportsBinaryRead') -> bool:
    return getattr(fp, 'seekable', lambda: False)()


class PDF:
    """A container for a PDF file to be signed and the signed version."""

    @overload
    def __init__(
        self,
        input_file: 'FileLike',
        *,
        out_stream: Optional[BinaryIO] = ...,
        sig_name: str = ...,
        sig_size: int = ...
    ): ...

    @overload
    def __init__(
        self,
        *,
        inout_stream: BinaryIO,
        sig_name: str = ...,
        sig_size: int = ...
    ): ...

    def __init__(
        self,
        input_file: Optional['FileLike'] = None,
        *,
        inout_stream: Optional[BinaryIO] = None,
        out_stream: Optional[BinaryIO] = None,
        sig_name: str = 'Signature',
        sig_size: int = 64*1024,  # 64 KiB
    ):
        """Accepts either a filename or a file-like object.

        It is the callers responsibility to ensure that buffers
        passed as `input_file` are pointing to the start of the file.
        We make no attempt to seek to the start of the file.

        :param inout_stream: Optional stream that will directly
        be used as both the input and output stream for in-place
        signing.

        :param out_stream: Optional stream that will be used to
        store the signed PDF. By default a BytesIO stream will
        be created to store the signed PDF.

        :param sig_name: Name of the Signature field to use. If
        no Signature with that name exists in the PDF, a new one
        will be created.

        :param sig_size: Size of the signature in DER encoding
        in bytes. By default 64KiB will be reserved, which should
        be enough for most cases right now.
        """

        in_place = out_stream is None
        writer_stream: 'SupportsBinaryRead'

        if isinstance(inout_stream, io.BytesIO):
            # in this case we create the signed version in-place
            # so the out_stream will be assigned the in_stream
            writer_stream = inout_stream
            assert out_stream is None

        elif input_file is None:
            raise ValueError('Either input_file or in_stream needs to be set')

        elif isinstance(input_file, str):
            # in this case we just read the entire file into a buffer
            # and create the signed version in-place
            with open(input_file, 'rb') as fp:
                writer_stream = io.BytesIO(fp.read())

        elif is_seekable(input_file):
            # in this case we can't assume that we're allowed to
            # create the signed version in-place, but we can allow
            # the IncrementalPdfFileWriter to operate on the input
            # file directly.
            writer_stream = input_file
            out_stream = out_stream or io.BytesIO()
            in_place = False

        else:
            # in this case we can't seek the input file so we need
            # to read the entire file into a buffer as well
            writer_stream = io.BytesIO(input_file.read())

        writer = IncrementalPdfFileWriter(writer_stream)
        self.cms_writer = cms_embedder.PdfCMSEmbedder().write_cms(
            field_name=sig_name,
            writer=writer
        )
        """CMS Writer used for embedding the signature"""
        next(self.cms_writer)

        self.sig_size = sig_size
        """Number of bytes reserved for the signature.
        It is the caller's responsibility to ensure that this is
        large enough to store the entire signature.

        Currently 64KiB (the default) appear to be enough. But
        the signature has been known to grow in size over the
        years.
        """

        if in_place:
            assert out_stream is None
            assert hasattr(writer_stream, 'write')
            out_stream = writer_stream  # type: ignore[assignment]

        self.sig_io_setup = cms_embedder.SigIOSetup(
            md_algorithm='sha256',
            in_place=in_place,
            output=out_stream
        )
        """Signing I/O setup to be passed to pyHanko"""

    @property
    def out_stream(self) -> BinaryIO:
        """Output stream for the signed PDF."""
        return self.sig_io_setup.output

    def digest(self) -> str:
        """Computes the PDF digest."""
        sig_obj = signers.SignatureObject(
            timestamp=datetime.now(),
            bytes_reserved=self.sig_size,
        )
        self.cms_writer.send(
            cms_embedder.SigObjSetup(
                sig_placeholder=sig_obj,
                mdp_setup=cms_embedder.SigMDPSetup(
                    md_algorithm='sha256',
                    certify=True,
                    docmdp_perms=fields.MDPPerm.NO_CHANGES,
                )
            )
        )
        digest, out_stream = self.cms_writer.send(self.sig_io_setup)
        assert out_stream is self.out_stream

        result = base64.b64encode(digest.document_digest)

        return result.decode('ascii')

    def write_signature(self, signature: bytes) -> None:
        """ Writes the signature into the pdf file.

        `digest` needs to be called first.

        :raises: :class:`SignatureTooLarge`: If sig_size is
        too small to store the entire signature.
        """
        signature_size = len(signature)*2  # account for hex encoding
        if signature_size > self.sig_size:
            raise SignatureTooLarge(signature_size)

        self.cms_writer.send(signature)
