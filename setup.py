# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = '0.2'

with open('README.rst') as readme:
    LONG_DESCRIPTION = ''.join(readme.readlines())

with open('requirements.txt') as f:
    REQUIRES = f.readlines()

DESCRIPTION = """Infrastrucutre metadata scraper with support for multiple
resource providers and tools for relationship analysis and visualization."""

setup(
    name='infra-scraper',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Aleš Komárek',
    author_email='ales.komarek@newt.cz',
    license='Apache License, Version 2.0',
    url='https://github.com/cznewt/infra-scraper/',
    packages=find_packages(),
    install_requires=REQUIRES,
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
