"""
Result definition
"""

from dataclasses import dataclass


@dataclass
class Result:
    """
    Internal result queue message
    """
    name: str
    time: float
    result: bool
