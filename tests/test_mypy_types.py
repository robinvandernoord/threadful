import pytest
import typing

from src.threadful import thread


@thread
def my_func() -> int:
    ...


@thread()
def my_func_parens() -> int:
    ...


@pytest.mark.mypy_testing
def test_stub():
    result1 = my_func()
    result2 = my_func_parens()
    typing.reveal_type()