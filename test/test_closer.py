"""
Test for Closer
"""
import time
from queue import Queue
from unittest.mock import AsyncMock, Mock

import pytest
from poor_man_redis_closer import Closer, Config, Result


@pytest.fixture
def config():
    conf = type('', (), {})()
    conf.interval = 1
    conf.num_checks = 3
    conf.stale_time = 15
    conf.max_queue_size = 100
    conf.local = 'local'
    conf.hosts = [{
        'name': 'local',
        'conn_kwargs': {},
    }, {
        'name': 'not-local-1',
        'conn_kwargs': {},
    }, {
        'name': 'not-local-2',
        'conn_kwargs': {},
    }]
    return conf


@pytest.mark.asyncio
async def test_opens_on_available(config):
    closer = Closer(config)
    await closer.setup()
    closer.closed = True
    closer.state['local']['conn'] = AsyncMock()
    for _ in range(config.num_checks):
        for host in config.hosts:
            closer.queue.put(Result(name=host['name'], time=0, result=True))
    await closer.process_queue()
    assert closer.closed is False


@pytest.mark.asyncio
async def test_closes_on_unavailable(config):
    closer = Closer(config)
    await closer.setup()
    closer.state['local']['conn'] = AsyncMock()
    for _ in range(config.num_checks):
        for host in config.hosts:
            closer.queue.put(Result(name=host['name'], time=0, result=False))
    await closer.process_queue()
    assert closer.closed is True
