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
    promise = slow(1).then(lambda it: it * 2).then(lambda it: it + 1).start()
    # manually started in the background, otherwise it would start once you call join() or result()
    time.sleep(2)
    assert promise.result().expect("2 > 1 so it should be done now") == 3


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

    err = promise.result().unwrap_err()
    assert isinstance(err, TypeError)

    promise = fails(0.5).catch(lambda err: 0)

    assert promise.join() == 0


def test_is_done():
    promise = slow(1)
    assert not promise.is_done()
    time.sleep(2)
    assert promise.is_done()

    promise = fails(1)
    assert not promise.is_done()
    time.sleep(2)
    assert promise.is_done()


def test_readme_examples():
    @thread  # with or without ()
    def some_function():
        time.sleep(4)
        return " done "

    # when ready, it sill call these callback functions.
    some_function().then(lambda result: result.strip()).then(lambda result: print(result))  # prints: "done"

    promise = some_function()  # ThreadWithResult[str] object
    print(promise.result())  # Err(None)
    time.sleep(5)  # after the thread is done:
    result = promise.result()
    print(result)  # Ok(" done ")
    assert result.expect("Expected value") == " done ", "Expected value"

    # alternative to sleep:
    result = promise.join()  # " done " if success, raises if the thread raised an exception

    @thread()
    def raises() -> str:
        raise ValueError()

    promise = raises().catch(lambda err: TypeError())

    with pytest.raises(TypeError):
        promise.join()

    result = promise.result()
    print(result)  # Err(TypeError)
    assert isinstance(result.expect_err("Expected TypeError"), TypeError), "Expected TypeError"

    promise = raises().catch(lambda err: "Something went wrong")

    print(promise.join())  # "Something went wrong"

    @thread()
    def fully_background() -> None:
        print('joe')

    fully_background().start()
