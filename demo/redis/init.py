#!/opt/closer/venv/bin/python
"""
Attach local redis to primary (or just start primary) and start sentinel
"""

import socket
import subprocess
import time

import redis

PRIMARY = 'host1'
TIMEOUT = 60


def start(program):
    """
    Start program with supervisor
    """
    subprocess.check_call(['supervisorctl', 'start', program])


def init_replica():
    """
    Run replicaof on local node when primary is ready
    """
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            primary_conn = redis.Redis(host=PRIMARY)
            primary_conn.ping()
            replica_conn = redis.Redis(host='localhost')
            replica_conn.replicaof(PRIMARY, '6379')
            return
        except Exception as exc:
            print('Init replica error:', repr(exc))
            time.sleep(1)


def _main():
    start('redis')
    start('sentinel')
    if socket.getfqdn() != PRIMARY:
        init_replica()
    start('closer')


if __name__ == '__main__':
    _main()
