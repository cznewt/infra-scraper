# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.2'

with open('README.rst') as readme:
    long_description = ''.join(readme.readlines())

setup(
    name='infra-scraper',
    version=version,
    description='Metadata scraper with support for Kubernetes, OpenStack, SaltStack, and Terraform resource providers.',
    long_description=long_description,
    author='Aleš Komárek',
    author_email='ales.komarek@newt.cz',
    license='Apache License, Version 2.0',
    url='https://github.com/cznewt/infra-scraper/',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'msgpack-python',
        'Flask',
        'Click',
        'os_client_config',
        'python-cinderclient',
        'python-glanceclient',
        'python-heatclient',
        'python-keystoneclient',
        'python-novaclient',
        'python-neutronclient',
        'pykube',
        'tosca-parser',
        'salt-pepper',
        'python-terraform',
        'graphviz'],
    extras_require={
        'tests': [
            'nose',
            'pycodestyle >= 2.1.0'],
        'docs': [
            'sphinx >= 1.4',
            'sphinx_rtd_theme']
    },
    classifiers=[
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'scraper_web = infra_scraper.cli:runserver',
            'scraper_status = infra_scraper.cli:status',
            'scraper_get = infra_scraper.cli:scrape',
            'scraper_get_forever = infra_scraper.cli:scrape_forever',
            'scraper_get_all = infra_scraper.cli:scrape_all',
            'scraper_get_all_forever = infra_scraper.cli:scrape_all_forever',
        ],
    },
)
