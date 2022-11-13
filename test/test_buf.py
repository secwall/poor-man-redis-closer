"""
Test for ring buffer
"""

from poor_man_redis_closer import RingBuf


def test_non_full_buffer():
    """
    Check that not full buffer works correctly
    """
    buf = RingBuf(4)
    for i in range(2):
        buf.add(i)
    assert buf.get() == [0, 1]


def test_full_buffer():
    """
    Check that full buffer works correctly
    """
    buf = RingBuf(4)
    for i in range(4):
        buf.add(i)
    assert buf.get() == [0, 1, 2, 3]


def test_overflow_buffer():
    """
    Check that full buffer with overflow works correctly
    """
    buf = RingBuf(4)
    for i in range(10):
        buf.add(i)
    assert buf.get() == [6, 7, 8, 9]
