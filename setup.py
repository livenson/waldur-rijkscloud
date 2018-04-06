#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'waldur-core>=0.157.2',
    'requests',
]


setup(
    name='waldur-rijkscloud',
    version='0.1.0.dev0',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='https://waldur.com',
    description='Waldur plugin for Dutch government cloud',
    long_description=open('README.md').read(),
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'waldur_extensions': (
            'waldur_rijkscloud = waldur_rijkscloud.extension:RijkscloudExtension',
        ),
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
