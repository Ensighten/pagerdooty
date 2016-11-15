#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Ensighten Pagerduty Config Backup',
    'author': 'Scott Cunningham',
    'url': 'https://github.org/ensighten/pagerdooty.git',
    'download_url': 'https://github.org/ensighten/pagerdooty.git',
    'author_email': 'infra@ensighten.com',
    'version': '1.0',
    'install_requires': ['hammock'],
    'packages': ['pagerdooty'],
    'scripts': ['bin/pagerdooty'],
    'name': 'pagerdooty'
}

setup(**config)
