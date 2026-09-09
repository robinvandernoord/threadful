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
# note: 'file' is deliberately not stored here; sys.stderr is looked up at call time
# so a stream replaced after import (pytest capture, logging wrappers) is respected.
_print_kwargs: dict[str, typing.Any] = dict(flush=True, end="\r", sep="")


def _stderr() -> typing.TextIO:
    """
    Resolve the output stream lazily, so replacing sys.stderr after import still works.
    """
    return sys.stderr


def _is_interactive() -> bool:
    """
    Whether the output stream can handle carriage returns and escape codes.

    False in CI, when piped or when redirected to a file. In that case, a carriage
    return is not a cursor move but (for most log viewers) a line break, so an
    animation would emit a new log line for every single frame.
    """
    stream = _stderr()
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):  # pragma: no cover
        # ValueError: I/O operation on closed file
        return False


def _print(*args: str, **kwargs: typing.Any) -> None:
    """
    Print to the (lazily resolved) stderr with the animation defaults applied.
    """
    print(*args, file=_stderr(), **(_print_kwargs | kwargs))


# https://stackoverflow.com/questions/5174810/how-to-turn-off-blinking-cursor-in-command-window


def hide_cursor() -> None:
    """
    Hides the cursor in the terminal.

    No-op when not attached to a terminal, otherwise the escape code would end up
    in the log or redirected file as garbage.
    """
    if not _is_interactive():
        return

    _print("\033[?25l", end="")
    atexit.register(show_cursor)  # clean up when the script ends


def show_cursor() -> None:
    """
    Shows the cursor in the terminal.

    No-op when not attached to a terminal (see hide_cursor).
    """
    if not _is_interactive():
        return

    _print("\033[?25h", end="")
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
    clear_with: typing.Optional[str] = None,
    animated: bool = True,
) -> T:
    return _animate(
        thread,
        text=text,
        speed=speed,
        animation=animation,
        clear_with=clear_with,
        animated=animated,
    )


def _animate(
    thread: ThreadWithReturn[T],
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = ("⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽", "⣾"),
    clear_with: typing.Optional[str] = None,
    animated: bool = True,
) -> T:
    """
    Private function to animate a loading spinner while a thread is running.

    Args:
        thread (ThreadWithReturn): The thread to animate.
        text (str): Extra text to show after the spinning icon.
        speed (float): The speed of the animation.
        animation (tuple): The frames of the animation.
        clear_with (str): replace the animation with a specific character instead of clearing the text line
        animated (bool): if False, plain log lines are written instead of an animation.

    Returns:
        T: The result of the thread.
    """
    if not animated:
        return _log(thread, text=text, speed=speed, clear_with=clear_with)

    idx = 0
    while not thread.is_done():
        idx += 1
        _text = text() if callable(text) else text
        _print(animation[idx % len(animation)], " ", _text)
        time.sleep(speed)

    # print enough spaces to clear text:
    _text = text() if callable(text) else text

    if clear_with:
        _print(clear_with, " ", _text, "\n")
    else:
        buffer_spaces = len(_text) + 1
        _print("\r ", " " * buffer_spaces)

    return thread.join()


def _log(
    thread: ThreadWithReturn[T],
    text: T_Text = "",
    speed: float = 0.05,
    clear_with: typing.Optional[str] = None,
) -> T:
    """
    Non-interactive counterpart of _animate: no spinner, no carriage returns.

    Every line ends in a real newline, and a line is only written when the text
    actually changed since the previous one. A static text therefore produces a
    single line, while a callback that reports progress produces one line per
    distinct value.

    Args:
        thread (ThreadWithReturn): The thread to wait for.
        text (str): Text to log, or a callback that's ran at every interval.
        speed (float): Seconds between checks.
        clear_with (str): prefix for the final line, marking completion.

    Returns:
        T: The result of the thread.
    """
    previous: typing.Optional[str] = None

    def emit(new: str, prefix: str = "") -> None:
        """Write a line, unless there's nothing to say."""
        nonlocal previous
        line = f"{prefix} {new}".strip() if prefix else new
        if line:
            _print(line, end="\n")
        previous = new

    while not thread.is_done():
        _text = text() if callable(text) else text
        if _text != previous:
            emit(_text)
        time.sleep(speed)

    _text = text() if callable(text) else text

    if clear_with:
        # the marker itself is new information, so always emit the closing line
        emit(_text, prefix=clear_with)
    elif _text != previous:
        emit(_text)

    return thread.join()


@typing.overload
def animate(
    thread: ThreadWithReturn[T],
    threaded: typing.Literal[True],
    text: T_Text = "",
    speed: float = 0.05,
    animation: tuple[str, ...] = (),
    clear_with: typing.Optional[str] = None,
    _hide_cursor: bool = True,
    force_animation: typing.Optional[bool] = None,
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
    clear_with: typing.Optional[str] = None,
    _hide_cursor: bool = True,
    force_animation: typing.Optional[bool] = None,
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
    clear_with: typing.Optional[str] = None,
    _hide_cursor: bool = True,
    force_animation: typing.Optional[bool] = None,
) -> T | ThreadWithReturn[T]:
    """
    Provides a pipx style loading animation for a thread.

    Args:
        thread (ThreadWithReturn): The thread to animate.
        text (str): Extra text to show after the spinning icon.
            This can be a static value or a callback that's ran at every interval.
        threaded (bool): Run the animation in a thread too, unblocking the main thread.
        speed (float): The speed of the animation (seconds between animation intervals, defaults to 50ms).
        animation (tuple): The frames of the animation.
        clear_with (str): replace the animation with a specific character instead of clearing the text line
        _hide_cursor (bool): If True, the cursor is hidden during the animation.
        force_animation (bool): By default, the animation is only shown on an interactive terminal;
            elsewhere (CI, pipes, redirects) plain log lines are written instead.
            Pass True or False to override that detection.

    Returns:
        T: The result of the thread.
    """
    animated = _is_interactive() if force_animation is None else force_animation

    # the cursor is only hidden because the spinner would make it jump around;
    # without an animation there's nothing to hide it for.
    with toggle_cursor(enabled=_hide_cursor and animated):
        kwargs: dict[str, typing.Any] = dict(
            text=text,
            speed=speed,
            animation=animation,
            clear_with=clear_with,
            animated=animated,
        )

        if threaded:
            return _animate_threaded(thread, **kwargs)
        else:
            return _animate(thread, **kwargs)
