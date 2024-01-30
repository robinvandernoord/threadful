import threading
import typing

from result import Err, Ok, Result

P = typing.ParamSpec("P")
R = typing.TypeVar("R")


class ThreadWithReturn(typing.Generic[R], threading.Thread):
    _target: typing.Callable[P, R]
    _args: P.args
    _kwargs: P.kwargs
    _return: R

    def __init__(self, target: typing.Callable[P, R], *a: typing.Any, **kw: typing.Any) -> None:
        kw["target"] = target
        super().__init__(*a, **kw)

    def run(self) -> None:
        try:
            if self._target is not None:
                self._return = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

    def result(self) -> "Result[R, None]":
        if self.is_alive():
            # still busy
            return Err(None)
        else:
            return Ok(self._return)


@typing.overload
def thread(my_function: typing.Callable[P, R]) -> typing.Callable[P, ThreadWithReturn[R]]:
    # code in this function is never executed, just shown for reference of the complex return type

    def wraps(*a: P.args, **kw: P.kwargs) -> ThreadWithReturn[R]:
        my_thread = ThreadWithReturn(target=my_function, args=a, kwargs=kw)
        my_thread.start()
        return my_thread

    return wraps


@typing.overload
def thread(
    my_function: None = None,
) -> typing.Callable[[typing.Callable[P, R]], typing.Callable[P, ThreadWithReturn[R]]]:
    # code in this function is never executed, just shown for reference of the complex return type

    def wraps(inner_function: typing.Callable[P, R]) -> typing.Callable[P, ThreadWithReturn[R]]:
        def inner(*a: P.args, **kw: P.kwargs) -> ThreadWithReturn[R]:
            my_thread = ThreadWithReturn(target=inner_function, args=a, kwargs=kw)
            my_thread.start()
            return my_thread

        return inner

    return wraps


def thread(
    my_function: typing.Callable[P, R] | None = None
) -> (
    typing.Callable[[typing.Callable[P, R]], typing.Callable[P, ThreadWithReturn[R]]]
    | typing.Callable[P, ThreadWithReturn[R]]
):
    # decorator

    if my_function is not None:

        def wraps(*a: P.args, **kw: P.kwargs) -> ThreadWithReturn[R]:
            my_thread = ThreadWithReturn(target=my_function, args=a, kwargs=kw)
            my_thread.start()
            return my_thread

        return wraps

    else:
        return thread


__all__ = [
    "ThreadWithReturn",
    "thread",
]
