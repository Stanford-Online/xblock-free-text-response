import json
import setuptools


package_json_file = open('package.json', 'r')
package_json = json.load(package_json_file)

setuptools.setup(
    name=package_json.get('name', 'xblock-test'),
    version=package_json.get('version', '0.1.0'),
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
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'freetextresponse = freetextresponse:Freetextresponse',
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
