"""
Very simple threading abstraction.
"""

import contextlib
import functools
import threading
import typing
from copy import copy

from result import Err, Ok, Result
from typing_extensions import Self

P = typing.ParamSpec("P")
R = typing.TypeVar("R")


class ThreadWithReturn(typing.Generic[R], threading.Thread):
    """
    Should not be used directly.

    Rather use the @thread decorator,
        which changes the return type of function() -> T into function() -> ThreadWithReturn[T]
    """

    _target: typing.Callable[P, R]
    _args: P.args
    _kwargs: P.kwargs
    _return: R | Exception
    _callbacks: list[typing.Callable[[R], R]]
    _catch: list[typing.Callable[[Exception | R], Exception | R]]

    def __init__(self, target: typing.Callable[P, R], *a: typing.Any, **kw: typing.Any) -> None:
        """
        Setup callbacks, otherwise same logic as super.

        'target' is explicitly mentioned outside of kw for type hinting.
        """
        kw["target"] = target
        super().__init__(*a, **kw)
        self._callbacks = []
        self._catch = []

    def start(self) -> Self:  # type: ignore
        """
        Normally, starting multiple times will lead to an error.

        This version ignores duplicate starts.
        """
        with contextlib.suppress(RuntimeError):
            super().start()
        return self

    def run(self) -> None:
        """
        Called in a new thread and handles the calling logic.
        """
        if self._target is None:  # pragma: no cover
            return

        try:
            result = self._target(*self._args, **self._kwargs)
            for callback in self._callbacks:
                result = callback(result)
            self._return = result
        except Exception as _e:
            e: Exception | R = _e  # make mypy happy
            for err_callback in self._catch:
                e = err_callback(e)
            self._return = e
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            self._callbacks.clear()
            self._catch.clear()
            del self._target, self._args, self._kwargs
            # keep self._return for .result()

    def result(self, wait: bool = False) -> "Result[R, Exception | None]":
        """
        Get the result value (Ok or Err) from the threaded function.

        By default, if the thread is not ready, Err(None) is returned.
        If `wait` is used, this functions like a join() but with a Result.

        """
        self.start()
        if wait:
            super().join()

        if self.is_alive():
            # still busy
            return Err(None)
        else:
            result = self._return
            if isinstance(result, Exception):
                return Err(result)
            else:
                return Ok(result)

    def is_done(self) -> bool:
        """
        Returns whether the thread has finished (result or error).
        """
        self.start()
        return not self.is_alive()

    def then(self, callback: typing.Callable[[R], R]) -> Self:
        """
        Attach a callback (which runs in the thread as well) on success.

        Returns 'self' so you can do .then().then().then().
        """
        new = copy(self)
        new._callbacks.append(callback)
        return new  # builder pattern

    def catch(self, callback: typing.Callable[[Exception | R], Exception | R]) -> Self:
        """
        Attach a callback (which runs in the thread as well) on error.

        You can either return a new Exception or a fallback value.
        Returns 'self' so you can do .then().catch().catch().
        """
        new = copy(self)
        new._catch.append(callback)
        return new

    def join(self, timeout: int | float | None = None) -> R:  # type: ignore
        """
        Enhanced version of thread.join that also returns the value or raises the exception.
        """
        self.start()
        super().join(timeout)

        match self.result():
            case Ok(value):
                return value
            case Err(exc):
                raise exc or Exception("Something went wrong.")

            # thread must be ready so Err(None) can't happen


@typing.overload
def thread(my_function: typing.Callable[P, R]) -> typing.Callable[P, ThreadWithReturn[R]]:  # pragma: no cover
    """
    Code in this function is never executed, just shown for reference of the complex return type.
    """

    def wraps(*a: P.args, **kw: P.kwargs) -> ThreadWithReturn[R]:
        """Idem ditto."""
        return ThreadWithReturn(target=my_function, args=a, kwargs=kw)  # code copied for mypy/ruff

    return wraps


@typing.overload
def thread(
    my_function: None = None,
) -> typing.Callable[[typing.Callable[P, R]], typing.Callable[P, ThreadWithReturn[R]]]:  # pragma: no cover
    """
    Code in this function is never executed, just shown for reference of the complex return type.
    """

    def wraps(inner_function: typing.Callable[P, R]) -> typing.Callable[P, ThreadWithReturn[R]]:
        """Idem ditto."""

        def inner(*a: P.args, **kw: P.kwargs) -> ThreadWithReturn[R]:
            """Idem ditto."""
            return ThreadWithReturn(target=inner_function, args=a, kwargs=kw)  # code copied for mypy/ruff

        return inner

    return wraps


def thread(
    my_function: typing.Callable[P, R] | None = None,
) -> (
    typing.Callable[[typing.Callable[P, R]], typing.Callable[P, ThreadWithReturn[R]]]
    | typing.Callable[P, ThreadWithReturn[R]]
):
    """
    This decorator can be used to automagically make functions threaded!

    Examples:
        @thread
        def myfunc():
            ...

        @thread()
        def otherfunc():
            ...

        myfunc() and otherfunc() now return a custom thread object,
            from which you can get the result value or exception with .result().
            This uses a Result (Ok or Err) type from rustedpy/result (based on the Rust Result type.)
            If the thread is not done yet, it will return Err(None)
            You can also call .join(), which waits (blocking) until the thread is done
            and then returns the return value or raises an exception (if raised in the thread)
    """
    if my_function is None:
        return thread

    @functools.wraps(my_function)
    def wraps(*a: P.args, **kw: P.kwargs) -> ThreadWithReturn[R]:
        # note: before it called .start() immediately here
        # however, if you then attach callbacks and the thread already finishes, they would not run.
        # now, start() is called once you check for a result() or wait for it to finish via join()
        return ThreadWithReturn(target=my_function, args=a, kwargs=kw)

    return wraps


def join_all_results(*threads: ThreadWithReturn[R]) -> tuple[Result[R, Exception], ...]:
    """
    Wait for all threads to complete and retrieve their results as `Result` objects.

    Args:
        *threads: A variable number of `ThreadWithReturn` instances to join.

    Returns:
        tuple[Result[R, Exception], ...]: A tuple containing `Result` objects for each thread,
        where each result represents the success or error outcome of the thread.
    """
    return tuple(_.result(wait=True) for _ in threads)


def join_all_or_raise(*threads: ThreadWithReturn[R]) -> tuple[R, ...]:
    """
    Wait for all threads to complete and retrieve their results, raising exceptions on failure.

    Args:
        *threads: A variable number of `ThreadWithReturn` instances to join.

    Returns:
        tuple[R, ...]: A tuple containing the successful results of each thread.

    Raises:
        Exception: If any thread raises an exception, it is propagated.
    """
    return tuple(_.join() for _ in threads)


def join_all_unwrap(*threads: ThreadWithReturn[R]) -> tuple[R | None, ...]:
    """
    Wait for all threads to complete and retrieve their results, unwrapping successes or returning None on error.

    Args:
        *threads: A variable number of `ThreadWithReturn` instances to join.

    Returns:
        tuple[R | None, ...]: A tuple containing the results of each thread, where errors are replaced with None.
    """
    return tuple(_.result(wait=True).unwrap_or(None) for _ in threads)


__all__ = [
    "ThreadWithReturn",
    "thread",
    "join_all_or_raise",
    "join_all_results",
    "join_all_unwrap",
]
