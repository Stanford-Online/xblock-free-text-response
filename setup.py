import os
from setuptools import setup
from setuptools.command.test import test as TestCommand

import json


package_json_file = open('package.json', 'r')
package_json = json.load(package_json_file)

class Tox(TestCommand):
    user_options = [('tox-args=', 'a', 'Arguments to pass to tox')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

setup(
    name=package_json.get('name', 'xblock-test'),
    version=package_json.get('version', '0.1.1'),
    description=package_json.get('description'),
    long_description=package_json.get('description'),
    author=package_json.get('author', {}).get('name'),
    author_email=package_json.get('author', {}).get('email'),
    url=package_json.get('homepage'),
    license='AGPL-3.0',
    packages=[
        'freetextresponse',
    ],
    install_requires=[
        'django',
        'django_nose',
        'mock',
        'coverage',
        'mako',
        'XBlock',
        'xblock-utils',
    ],
    dependency_links=[
        'https://github.com/edx/xblock-utils/tarball/c39bf653e4f27fb3798662ef64cde99f57603f79#egg=xblock-utils',
    ],
    entry_points={
        'xblock.v1': [
            'freetextresponse = freetextresponse:FreeTextResponse',
        ],
    },
    package_dir={
        'freetextresponse': 'freetextresponse',
    },
    package_data={
        "freetextresponse": [
            'public/*',
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
)
