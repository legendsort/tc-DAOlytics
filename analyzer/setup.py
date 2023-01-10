#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='rndao-analyzer',
    version='1.0.0',
    author='Simon Sekavčnik, RnDAO',
    maintainer='Simon Sekavčnik',
    maintainer_email='simon.sekavcnik@gmail.com',
    packages= find_packages(),
    description='Automatic analysis of the dao',
    long_description=open('README.md').read(),
    install_requires=[
        "pytest",
    ],
)
