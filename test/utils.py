"""
Test utils
"""
from unittest.mock import AsyncMock, Mock

import pytest


class Finish(Exception):
    """
    Finish class for tests
    """


@pytest.fixture
def sleep_finish(mocker):
    mock = AsyncMock(side_effect=Finish)
    mocker.patch('asyncio.sleep', side_effect=mock)


async def async_hack():
    pass


@pytest.fixture
def mock_conn(mocker):
    mock = Mock()
    mock.__await__ = lambda x: async_hack().__await__()
    mock.return_value.ping = AsyncMock()
    mocker.patch('redis.asyncio.Redis', mock)
    return mock
