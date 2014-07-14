#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='python-hwinfo',
    author='Rob Dobson',
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
