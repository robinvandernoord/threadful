import typing

import pytest

from src.threadful import thread


@thread
def my_func() -> int:
    return 123


@thread()
def my_func_parens() -> int:
    return 321


T = typing.TypeVar("T")


@thread
def my_func_args(first: str, second: T) -> T:
    return second


@thread()
def my_func_args_parens(first: str, second: T) -> T:
    return second


@pytest.mark.mypy_testing
def test_stub() -> None:
    result1 = my_func()
    result2 = my_func_parens()
    typing.reveal_type(result1.result().unwrap())  # R: builtins.int
    typing.reveal_type(result2.result().unwrap())  # R: builtins.int

    typing.reveal_type(my_func_args("", 0).join())  # R: builtins.int
    typing.reveal_type(my_func_args_parens("", 0).join())  # R: builtins.int
