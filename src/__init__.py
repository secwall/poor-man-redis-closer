"""
Console entry-point
"""

import logging
from argparse import ArgumentParser

from .buf import RingBuf
from .closer import Closer
from .config import Config
from .conn import Connection
from .result import Result

__all__ = [
    'Closer',
    'Config',
    'Connection',
    'Result',
    'RingBuf',
]


def _main():
    parser = ArgumentParser()
    parser.add_argument('-c',
                        '--config',
                        type=str,
                        default='/etc/redis-closer.yaml',
                        help='config path')
    parser.add_argument('-v',
                        '--verbose',
                        default=0,
                        action='count',
                        help='Be verbose')
    args = parser.parse_args()

    conf = Config(args.config)

    logging.basicConfig(
        level=(logging.ERROR - 10 * (min(3, args.verbose))),
        format='%(asctime)s %(name)-16s %(levelname)-8s: %(message)s')

    closer = Closer(conf)

    closer.start()
