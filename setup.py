#!/usr/bin/env python

# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

from setuptools import setup, find_packages
import os

SRC_DIR = "src"
MODULE_NAME = "midonet_sandbox"
__version__ = 1.0

with open('./requirements.txt') as reqs_txt:
    requirements = [line for line in reqs_txt]


def assets():
    assets_path = \
        os.path.join(os.path.dirname(__file__), SRC_DIR, MODULE_NAME, 'assets')

    assets_list = list()
    for root, dirs, files in os.walk(assets_path):
        for file in files:
            assets_list.append(os.path.join(root, file).replace(
                "{}/{}/".format(SRC_DIR, MODULE_NAME), ""))

    return assets_list

# with open('./test-requirements.txt') as test_reqs_txt:
# test_requirements = [line for line in test_reqs_txt]

setup(
    name=MODULE_NAME,
    version=__version__,
    description="Sandobox framework for Midonet",
    url='https://github.com/midonet/midonet-sandbox',
    package_dir={"": SRC_DIR},
    packages=find_packages(SRC_DIR, exclude=["tests"]),
    package_data={'': assets()},
    install_requires=requirements,
    # tests_require=test_requirements,
    zip_safe=False,
    # test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points="""
    [console_scripts]
    sandbox-manage=midonet_sandbox.cli.cli:main
    """,
)
