.. :changelog:

Release History
---------------

2.3.0 (2024-08-21)
++++++++++++++++++

- Add Python 3.11, 3.12, 3.13 support
- Remove Python 3.7 support

2.2.1 (2022-09-02)
++++++++++++++++++

- Gracefully handles empty batches

2.2.0 (2022-07-14)
++++++++++++++++++

- Switches to AIS API Profile 1.1

2.1.2 (2022-07-14)
++++++++++++++++++

- Actually fixes batch signing

2.1.1 (2022-07-14)
++++++++++++++++++

- Fix batch signing

2.1.0 (2022-04-19)
++++++++++++++++++

- Clean up project structure
- Clean up PDF API
- Clean up docs

2.0.0 (2022-04-12)
++++++++++++++++++

- Creation of AIS2.py fork
- Replaced Travis CI with GitHub Actions.

0.3.0-beta (2021-11-04)
+++++++++++++++++++++++

- Remove Python 2.7, 3.4, 3.5, 3.6 support
- Replace PyPDF2 and itext with pyHanko
- Remove support for signing prepared PDFs

0.2.2 (2018-10-22)
++++++++++++++++++

- Store the last created request_id on the AIS instance
- Use a proper test matrix on Travis to test various Python releases
- Add Python 3.6 to test matrix

0.2.1 (2016-06-16)
++++++++++++++++++

- Return in batch mode timestamp and revocation information with the signature.
- Fix python3 bugs.
- Refactoring.

0.2.0 (2016-05-19)
++++++++++++++++++

**Documentation**

- Added sections for introduction, installation, testing, project status, API
  reference.

0.1 (2016-05-17)
++++++++++++++++

Initial release. It is possible to start with a batch of pdf files that do not
yet have a prepared signature, and sign them.
