"""
Connection coroutine
"""

import asyncio
import logging
import time
from queue import Full

import redis.asyncio as redis

from .result import Result


class Connection:  # pylint: disable=too-few-public-methods
    """
    Connection coroutine worker
    """

    def __init__(self, name, interval, status_queue, **conn_kwargs):
        self.name = name
        self.interval = interval
        self.queue = status_queue
        self.conn_kwargs = conn_kwargs
        self.conn = None
        self.log = logging.getLogger(
            f'conn-{self.conn_kwargs.get("host", "localhost")}:'
            f'{self.conn_kwargs.get("port", 6379)}')

    def _send_message(self, result):
        try:
            self.queue.put(
                Result(name=self.name, time=time.time(), result=result))
        except Full:
            self.log.error('Unable to report result %s: queue is full', result)

    async def start(self):
        """
        Start coroutine
        """
        while True:
            try:
                if not self.conn:
                    self.conn = redis.Redis(**self.conn_kwargs)
                await self.conn.ping()
                self.log.debug('Ping ok')
                self._send_message(True)
            except Exception as exc:
                self.log.error('Got an error: %r', exc)
                self._send_message(False)
            await asyncio.sleep(self.interval)
