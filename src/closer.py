"""
Main closer logic
"""

import asyncio
import logging
import time
from queue import Queue

from .buf import RingBuf
from .conn import Connection


class Closer:
    """
    Redis closer
    """

    def __init__(self, config):
        self.config = config
        self.state = {}
        self.log = logging.getLogger('closer')
        self.queue = Queue(maxsize=config.max_queue_size)
        self.closed = False

    def start(self):
        """
        Start closer
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.main())

    async def setup(self):
        """
        Setup state
        """
        has_local = False
        for host in self.config.hosts:
            if host['name'] == self.config.local:
                has_local = True
                host['conn_kwargs']['host'] = 'localhost'
            conn = Connection(host['name'], self.config.interval, self.queue,
                              **host['conn_kwargs'])
            if host['name'] in self.state:
                raise RuntimeError(f'Duplicate conn: {host["name"]}')
            self.state[host['name']] = {
                'conn': conn,
                'last_ts': time.time(),
                'buf': RingBuf(self.config.num_checks),
            }
        if not has_local:
            raise RuntimeError(f'Invalid config: no node {self.config.local}')

    async def main(self):
        """
        Main closer coroutine
        """
        await self.setup()
        for state in self.state.values():
            state['task'] = asyncio.create_task(state['conn'].start())
        while True:
            await self.process_queue()
            await asyncio.sleep(self.config.interval)

    async def process_queue(self):
        """
        Handle events from queue and decide if we should close local node
        """
        while not self.queue.empty():
            item = self.queue.get()
            state = self.state[item.name]
            self.log.debug('Processing result at %s for %s: %s', item.time,
                           item.name, item.result)
            state['buf'].add(item.result)
            state['last_ts'] = item.time

        now = time.time()
        available = set()
        for name, state in self.state.items():
            failures = sum(1 for x in state['buf'].get() if not x)
            if failures != self.config.num_checks and \
                    state['last_ts'] - now < self.config.stale_time:
                self.log.debug('%s is available', name)
                available.add(name)
            else:
                self.log.info('%s is not available', name)

        if len(available) < len(self.state) // 2 + 1:
            self.log.info('Less than majority of hosts available')
            if not self.closed:
                self.log.info('Closing')
                await self.close()
        elif self.closed:
            self.log.info('Opening')
            await self.open()

    async def is_primary(self, node):
        """
        Check if node is primary
        """
        try:
            conn = self.state[node]['conn'].conn
            info = await conn.info('repliation')
            return info['role'] == 'master'
        except Exception as exc:
            self.log.error('Unable to check %s: %r', node, exc)

    async def close(self):
        """
        Close local redis
        """
        try:
            conn = self.state[self.config.local]['conn'].conn
            await conn.config_set('protected-mode', 'yes')
            await conn.client_kill_filter(_type='normal')
            await conn.client_kill_filter(_type='pubsub')
            self.closed = True
        except Exception as exc:
            self.log.error('Unable to close: %r', exc)

    async def open(self):
        """
        Open local redis
        """
        try:
            found_primary = None
            for node in self.state:
                if node == self.config.local:
                    continue
                if await self.is_primary(node):
                    if not found_primary:
                        found_primary = node
                        continue
                    raise RuntimeError(
                        f'Multiple primaries: {node} and {found_primary}')
            conn = self.state[self.config.local]['conn'].conn
            if found_primary:
                await conn.replicaof(
                    found_primary,
                    self.config.hosts[found_primary]['conn_kwargs'].get(
                        'port', 6379))
            await conn.config_set('protected-mode', 'no')
            self.closed = False
        except Exception as exc:
            self.log.error('Unable to open: %r', exc)
