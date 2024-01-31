import pytest
import typing

from src.threadful import thread


@thread
def my_func() -> int:
    return 123


@thread()
def my_func_parens() -> int:
    return 321


@pytest.mark.mypy_testing
def test_stub() -> None:
    result1 = my_func()
    result2 = my_func_parens()
    typing.reveal_type(result1.result().unwrap())  # R: builtins.int
    typing.reveal_type(result2.result().unwrap())  # R: builtins.int
