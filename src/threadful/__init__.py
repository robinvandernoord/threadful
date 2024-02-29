"""
This file exposes the most important functions of this library.
"""

from .bonus import animate
from .core import ThreadWithReturn, thread

threadify = thread

__all__ = [
    "ThreadWithReturn",
    "thread",
    "threadify",
    "animate",
]
