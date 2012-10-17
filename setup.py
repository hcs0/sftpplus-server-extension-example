"""
Package definition for sftpplus-server-extension-example.
"""
from setuptools import setup

VERSION = u'0.1.0'

setup(
    name='sftpplus-server-extension-example',
    version=VERSION,
    maintainer="Adi Roiban",
    maintainer_email="adi.roiban@chevah.com",
    license='PUblic Domain License',
    platforms='any',
    description='SFTPPlus Server extension example.',
    long_description=open('README').read(),
    url='http://www.sftpplus.com',
    packages=['example_extension'],
)
