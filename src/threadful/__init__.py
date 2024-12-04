"""
This file exposes the most important functions of this library.
"""

from .bonus import animate
from .core import ThreadWithReturn, join_all_or_raise, join_all_results, join_all_unwrap, thread

threadify = thread

__all__ = [
    "ThreadWithReturn",
    "thread",
    "threadify",
    "animate",
    "join_all_unwrap",
    "join_all_results",
    "join_all_or_raise",
]
