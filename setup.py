# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-NowPlayingTouch',
    version=get_version('mopidy_nowplayingtouch/__init__.py'),
    url='https://github.com/kdbdallas/mopidy-nowplayingtouch',
    license='Apache License, Version 2.0',
    author='Dallas Brown',
    author_email='dbrown@port21.com',
    description='A Frontend Mopidy extension for the Mopidy Music Server and the Pi MusicBox for use with a Touch Screen.',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
        'pygame'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'nowplayingtouch = mopidy_nowplayingtouch:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
