"""
Test for Connection
"""
from queue import Queue

import pytest
from poor_man_redis_closer import Connection
from .utils import Finish, sleep_finish, mock_conn


@pytest.mark.asyncio
async def test_conn_emits_true_on_success(sleep_finish, mock_conn):
    queue = Queue()
    conn = Connection('test', 1, queue)
    with pytest.raises(Finish):
        await conn.start()
    assert queue.get_nowait().result is True


@pytest.mark.asyncio
async def test_conn_emits_false_on_fail(sleep_finish, mock_conn):
    queue = Queue()
    mock_conn.ping.side_effect = RuntimeError
    conn = Connection('test', 1, queue)
    with pytest.raises(Finish):
        await conn.start()
    assert not queue.get_nowait().result is False
