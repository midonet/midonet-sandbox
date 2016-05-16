#!/usr/bin/env python

# Copyright (c) 2015 Midokura SARL, All Rights Reserved.
#
# @author: Antonio Sagliocco <antonio@midokura.com>, Midokura

from setuptools import setup, find_packages
import os

SRC_DIR = "src"
MODULE_NAME = "midonet_sandbox"
__version__ = 1.0

def assets():
    assets_path = \
        os.path.join(os.path.dirname(__file__), SRC_DIR, MODULE_NAME, 'assets')

    assets_list = list()
    for root, dirs, files in os.walk(assets_path):
        for file in files:
            assets_list.append(os.path.join(root, file).replace(
                "{}/{}/".format(SRC_DIR, MODULE_NAME), ""))

    return assets_list

setup(
    name=MODULE_NAME,
    version=__version__,
    description="Sandobox framework for Midonet",
    url='https://github.com/midonet/midonet-sandbox',
    package_dir={"": SRC_DIR},
    packages=find_packages(SRC_DIR, exclude=["tests"]),
    package_data={'': assets()},
    install_requires=['docker-compose==1.3.1',
                      'dockerfile-parse==0.0.5',
                      'docopt==0.6.2',
                      'tabulate==0.7.5',
                      'humanize==0.5.1',
                      'PyYAML==3.11',
                      'injector==0.9.1'],
    zip_safe=False,
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
    sandbox-manage=midonet_sandbox.logic.cli:main
    """,
)
