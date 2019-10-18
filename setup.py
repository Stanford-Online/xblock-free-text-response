"""
A configurable, open text-type response
"""
from os import path
from setuptools import setup


version = '1.0.1'
description = __doc__.strip().split('\n')[0]
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst')) as file_in:
    long_description = file_in.read()


setup(
    name='xblock-free-text-response',
    version=version,
    description=description,
    long_description=long_description,
    author='stv',
    author_email='stv@stanford.edu',
    url='https://github.com/Stanford-Online/xblock-free-text-response',
    license='AGPL-3.0',
    packages=[
        'freetextresponse',
    ],
    install_requires=[
        'Django<2.0.0',
        'enum34',
        'six',
        'XBlock',
        'xblock-utils',
    ],
    entry_points={
        'xblock.v1': [
            'freetextresponse = freetextresponse.xblocks:FreeTextResponse',
        ],
    },
    package_dir={
        'freetextresponse': 'freetextresponse',
    },
    package_data={
        "freetextresponse": [
            'mixins/*.py',
            'public/*',
            'scenarios/*.xml',
            'templates/*',
        ],
    },
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTTP',
    ],
    test_suite='freetextresponse.tests',
    tests_require=[
        'ddt',
        'edx-opaque-keys',
        'mock',
    ],
)
