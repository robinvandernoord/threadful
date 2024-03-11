"""
Fun little util features.

This module provides utility functions for cursor management and thread animation.

Attributes:
    _print_kwargs (dict): A dictionary of keyword arguments for the print function.
"""

import atexit
import sys
import time
import typing
from contextlib import contextmanager

from .core import ThreadWithReturn
from .core import thread as threadify

T = typing.TypeVar("T")
_print_kwargs: dict[str, typing.Any] = dict(file=sys.stderr, flush=True, end="\r", sep="")


# https://stackoverflow.com/questions/5174810/how-to-turn-off-blinking-cursor-in-command-window


def hide_cursor() -> None:
    """
    Hides the cursor in the terminal.
    """
    print("\033[?25l", end="", flush=True)
    atexit.register(show_cursor)  # clean up when the script ends


def show_cursor() -> None:
    """
    Shows the cursor in the terminal.
    """
    print("\033[?25h", end="", flush=True)
    atexit.unregister(show_cursor)  # clean up no longer required


@contextmanager
def toggle_cursor(enabled: bool = True) -> typing.Generator[None, None, None]:
    """
    Toggles the visibility of the cursor in the terminal.

    Args:
        enabled (bool): If True, the cursor is shown, otherwise it is hidden.
    """
    if not enabled:
        yield
        return

    hide_cursor()
    yield
    show_cursor()


T_Text: typing.TypeAlias = str | typing.Callable[[], str]


@threadify
def _animate_threaded(
    thread: ThreadWithReturn[T],
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = ("⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽", "⣾"),
) -> T:
    return _animate(thread, text, speed, animation)


def _animate(
    thread: ThreadWithReturn[T],
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = ("⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽", "⣾"),
) -> T:
    """
    Private function to animate a loading spinner while a thread is running.

    Args:
        thread (ThreadWithReturn): The thread to animate.
        speed (float): The speed of the animation.
        animation (tuple): The frames of the animation.

    Returns:
        T: The result of the thread.
    """
    idx = 0
    while not thread.is_done():
        idx += 1
        _text = text() if callable(text) else text
        print(animation[idx % len(animation)], " ", _text, **_print_kwargs)
        time.sleep(speed)

    # print enough spaces to clear text:
    _text = text() if callable(text) else text
    buffer_spaces = len(_text) + 1
    print("\r ", " " * buffer_spaces, **_print_kwargs)
    return thread.join()


@typing.overload
def animate(
    thread: ThreadWithReturn[T],
    threaded: typing.Literal[True],
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = (),
    _hide_cursor: bool = True,
) -> ThreadWithReturn[T]:
    """
    Pass threaded=True to also thread the loading animation, clearing up the thread.
    """


@typing.overload
def animate(
    thread: ThreadWithReturn[T],
    threaded: typing.Literal[False] = False,
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = (),
    _hide_cursor: bool = True,
) -> T:
    """
    Default behavior: run the animation sync.
    """


def animate(
    thread: ThreadWithReturn[T],
    threaded: bool = False,
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = ("⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽", "⣾"),
    _hide_cursor: bool = True,
) -> T | ThreadWithReturn[T]:
    """
    Provides a pipx style loading animation for a thread.

    Args:
        thread (ThreadWithReturn): The thread to animate.
        text (str): Extra text to show after the spinning icon
        threaded (bool): Run the animation in a thread too, unblocking the main thread.
        speed (float): The speed of the animation.
        animation (tuple): The frames of the animation.
        _hide_cursor (bool): If True, the cursor is hidden during the animation.

    Returns:
        T: The result of the thread.
    """
    with toggle_cursor(enabled=_hide_cursor):
        if threaded:
            return _animate_threaded(thread, text, speed, animation)
        else:
            return _animate(thread, text, speed, animation)
