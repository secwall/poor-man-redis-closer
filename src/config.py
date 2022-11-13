"""
Closer config
"""

import socket

import yaml


class Config:  # pylint: disable=too-few-public-methods
    """
    Closer config
    """

    def __init__(self, path):
        with open(path, encoding='utf-8') as inp:
            data = yaml.safe_load(inp)
        self.interval = data.get('interval', 1)
        self.num_checks = data.get('num_checks', 3)
        self.stale_time = data.get('stale_time', 15)
        self.max_queue_size = data.get('max_queue_size', 1000)
        self.local = data.get('local', socket.getfqdn())
        self.hosts = data['hosts']
