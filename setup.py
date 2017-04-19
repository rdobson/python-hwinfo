#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='python-hwinfo',
    author='Rob Dobson',
    author_email = 'rob@rdobson.co.uk',
    version = '0.1.7',
    description = 'Library for parsing hardware info on Linux OSes.',
    url = 'https://github.com/rdobson/python-hwinfo',
    download_url = 'https://github.com/rdobson/python-hwinfo/tarball/0.1.7',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'hwinfo = hwinfo.tools.inspector:main',
        ]
    },
    install_requires = [
        'paramiko',
        'prettytable',
    ],
    )
