sftpplus-server-extension-example
=================================

Example implementation for SFTPPlus Server extension.

This can be used as the base for implementing custom extensions.

Feel free to rename the "example_extension" folder and "example.py" file,
to something more creative.


Installation
------------

To install this package use:

$ cd PATH_TO_EXTENSION_CODE
$ PATH/TO/SFTPPLUS/SERVER/bin/python setup.py install

You need to use the verion of Python distributed with the SFTPPlus Server.
This will install the package in the server's library folders. Otherwise the
extension will be installed in the system-wide Python version.

Installing the extension using system Python version is not supported.
