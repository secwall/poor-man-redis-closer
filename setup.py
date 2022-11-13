#!/usr/bin/env python
"""
setup.py for poor-man-redis-closer
"""
# pylint: skip-file

from setuptools import setup

REQUIREMENTS = [
    'redis == 4.3.4',
    'pyyaml >= 6.0',
]

setup(
    name='poor-man-redis-closer',
    version='0.0.1',
    description='A simple demo for closing partitioned redis primary',
    license='MIT',
    url='https://github.com/secwall/poor-man-redis-closer',
    author='secwall',
    author_email='secwall@secwall.me',
    maintainer='secwall',
    maintainer_email='secwall@secwall.me',
    zip_safe=False,
    platforms=['Linux', 'BSD', 'MacOS'],
    packages=['poor_man_redis_closer'],
    package_dir={'poor_man_redis_closer': 'src'},
    entry_points={'console_scripts': [
        'poor-man-redis-closer = poor_man_redis_closer:_main',
    ]},
    install_requires=REQUIREMENTS,
)
