import time
import typing
import pytest

from src.threadful import thread

T = typing.TypeVar("T")

N = typing.TypeVar("N", int, float)

@thread
def slow(value: N) -> N:
    time.sleep(value)
    return value

@thread()
def fails(wait: N) -> N:
    time.sleep(wait)
    if wait > 0:
        raise ValueError("This function should fail.")
    return wait

def test_threading():
    promise = slow(0.5)
    assert promise.result().is_err
    time.sleep(1)
    assert promise.result().is_ok
    assert promise.result().unwrap() == 0.5


def test_callback():
    promise = slow(1).then(lambda it: it * 2).then(lambda it: it + 1)
    time.sleep(1.5)
    assert promise.result().unwrap() == 3

def test_join():
    assert slow(1).then(lambda it: 0).join() == 0


def test_error():
    promise = fails(1)

    assert promise.result().is_err
    print(
        promise.result().unwrap_err()
    )

    with pytest.raises(ValueError):
        promise.join()

    promise = fails(0.5).catch(lambda e: TypeError(f"new error type from {e}"))

    with pytest.raises(TypeError):
        promise.join()

    promise = fails(0.5).catch(lambda err: 0)

    assert promise.join() == 0

