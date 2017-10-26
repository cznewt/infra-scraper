# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.1'

with open('README.rst') as readme:
    long_description = ''.join(readme.readlines())

setup(
    name='infra-scraper',
    version=version,
    description='Infrastructure metadata scraper with support for Kubernetes, OpenStack ans SaltStack.',
    long_description=long_description,
    author='Aleš Komárek',
    author_email='ales.komarek@newt.cz',
    license='MIT',
    url='https://github.com/cznewt/infra-scraper/',
    packages=find_packages(),
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
            'scraper_web = infra_scraper.server:run',
            'scraper_status = infra_scraper.cli:status',
            'scraper_get = infra_scraper.cli:scrape',
            'scraper_get_all = infra_scraper.server:scrape_all',
        ],
    },
)
