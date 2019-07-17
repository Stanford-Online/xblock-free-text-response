Free Text Response XBlock
================================

XBlock to capture a free-text response.

|badge-travis|
|badge-coveralls|

This package provides an XBlock for use with the EdX Platform and makes
it possible for instructors to create questions that expect a
free-text response.


Installation
------------


System Administrator
~~~~~~~~~~~~~~~~~~~~

To install the XBlock on your platform,
add the following to your `requirements.txt` file:

    xblock-free-text-response

You'll also need to add this to your `INSTALLED_APPS`:

    freetextresponse


Course Staff
~~~~~~~~~~~~

To install the XBlock in your course,
access your `Advanced Module List`:

    Settings -> Advanced Settings -> Advanced Module List

and add the following:

    freetextresponse



.. |badge-coveralls| image:: https://coveralls.io/repos/github/Stanford-Online/xblock-free-text-response/badge.svg?branch=master
   :target: https://coveralls.io/github/Stanford-Online/xblock-free-text-response?branch=master
.. |badge-travis| image:: https://travis-ci.org/Stanford-Online/xblock-free-text-response.svg?branch=master
   :target: https://travis-ci.org/Stanford-Online/xblock-free-text-response
