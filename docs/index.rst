.. AIS.py documentation master file, created by
   sphinx-quickstart on Wed May 18 11:35:35 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

AIS2.py
======

AIS.py: a Python interface for the Swisscom All-in Signing Service (aka AIS).

AIS2.py is a fork created to get rid of the licensing woes affected itext dependency and replace it with pyHanko. Furthermore the API was slightly adjusted to be more flexible, so buffers can be passed around rather than files that need to exist on the filesystem.

Release v\ |version|.

AIS2.py works like this::

    >>> from AIS import AIS, PDF
    >>> client = AIS('alice', 'a_secret', 'a.crt', 'a.key')
    >>> pdf = PDF('source.pdf')
    >>> ais.sign_one_pdf(pdf)
    >>> with open('target.pdf', 'wb') as fp:
    ...     fp.write(pdf.out_stream.getvalue())
    ...

AIS is a webservice for electronic signatures offered by Swisscom. You can
check out the `corporate page`_ and the `reference guide`_ of the
service.

To use the webservice you have to send an appropriate digest of the file. The
service returns a PKCS#7 detached signature that can be send alongside the
original file.

To validate a detached signature, the digest of the original file can be
computed again.

In the case of PDF files, the signature is integrated in the PDF itself and
it needs to be extracted to be verified.

A complication in that case is that during verification you must be able to
compute the same digest that was used to generate the signature with the
original file, but the original file is not available anymore, and the signed
file has clearly a different digest.

Thus, the procedure is the following:

1. The original PDF file is prepared by adding an empty signature block. This
   includes a ``ByteRange`` object.
2. The digest is computed only in the part specified by the ``ByteRange``, so
   it excludes the empty signature.
3. The digest is sent to the AIS webservice.
4. The detached signature is included in the placeholder.

``AIS.py`` takes care of all this, delegating everything put step 3 to `pyHanko`_.

.. _corporate page:  https://www.swisscom.ch/en/business/enterprise/offer/security/identity-access-security/signing-service.html
.. _reference guide: http://documents.swisscom.com/product/1000255-Digital_Signing_Service/Documents/Reference_Guide/Reference_Guide-All-in-Signing-Service-en.pdf
.. _pyHanko: https://github.com/MatthiasValvekens/pyHanko

Installation
------------

Make sure you have Python 3.7, 3.8, 3.9, 3.11 or a recent Pypy
then::

    $ pip install AIS2.py

This will pull Python dependencies, you don't need to install anything other than Python.

Tests
-----

A few tests are found in the ``tests/`` directory. Integration tests use the
real webservice, and HTTP requests/responses are recorded with the `vcrpy`_
library as cassettes. This means that you can run all the tests on your machine
without real credentials to AIS. The sensible part of the request (i.e. the
login and password) is hidden automatically from the cassette file. This also
allows the tests to run on GitHub Actions.

To run the tests locally, enter the directory you cloned and::

    $ pip install tox
    $ tox

Tox will automatically create a virtualenv for each Python version, install the
package and run the tests.

If you prefer to do this manually for one Python version::

    $ python -m virtualenv env
    $ source env/bin/activate
    $ pip install -e .
    $ py.test

.. _vcrpy: https://github.com/kevin1024/vcrpy

Status
------

AIS2.py is already functional for its main use case, but a few things could be
improved:

- Allow to request only a trusted timestamp instead of a signature.
- Allow to choose a different digest algorithm than SHA256.
- Handle second factor authentication in addition to static certificates.
- Find a way to check PDF signatures programmatically in the tests.
- Document all parameters and return values in the docstrings (i.e. improve
  the API reference).

API Reference
-------------

This section describes classes and exceptions.

.. toctree::
   :maxdepth: 2

   api

.. include:: ../HISTORY.rst

.. include:: ../AUTHORS.rst

License
-------

Copyright (C) 2016 Camptocamp SA

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

