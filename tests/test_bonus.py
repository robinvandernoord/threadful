import contextlib
import io
import sys
import time
from datetime import datetime

from threadful import animate, thread
from threadful.bonus import hide_cursor, show_cursor, toggle_cursor


@thread
def wait(duration: int):
    import time

    time.sleep(duration)
    return duration


def test_animate():
    input_duration = 3
    t = "waiting sync"
    output_duration = animate(wait(input_duration), text=t)

    assert input_duration == output_duration

    print("done :)")


def test_animate_async():
    input_duration = 3
    output_thread = animate(
        wait(input_duration),
        threaded=True,
    )

    hide_cursor()
    t = "  animating in thread"
    print(t, file=sys.stderr, flush=True, end="\r")

    assert not output_thread.is_done()

    output_duration = output_thread.join()

    assert input_duration == output_duration

    # extra newline so it's below 'animating in thread':
    print("\ndone :)")


def test_animate_callback():
    def text():
        return str(datetime.now())

    animate(
        wait(1),
        text=text,
    )


def test_clear_with():
    animate(
        wait(1),
        text="running",
        clear_with="✓",
    )


def test_toggle_cursor():
    with toggle_cursor(True):
        pass
    with toggle_cursor(False):
        pass


if __name__ == "__main__":
    # print('1. sync')
    # test_animate()
    # print('2. async')
    # test_animate_async()
    # print('3. with callback')
    test_animate_callback()
    print("4. done")


class FakeStream(io.StringIO):
    """A StringIO that can pretend to be (or not be) a terminal."""

    def __init__(self, interactive: bool):
        super().__init__()
        self._interactive = interactive

    def isatty(self) -> bool:
        return self._interactive


@contextlib.contextmanager
def capture(interactive: bool = False):
    """Replace sys.stderr *after* import, to also cover the lazy stream lookup."""
    stream = FakeStream(interactive)
    original, sys.stderr = sys.stderr, stream
    try:
        yield stream
    finally:
        sys.stderr = original


@thread
def counter(steps: list[int], amount: int = 5):
    for i in range(amount):
        steps.append(i + 1)
        time.sleep(0.02)
    return amount


def test_no_animation_when_not_a_terminal():
    """Static text should produce exactly one line and no carriage returns."""
    with capture() as stream:
        assert animate(wait(1), text="loading") == 1

    value = stream.getvalue()
    assert value == "loading\n"
    assert "\r" not in value
    assert "\033" not in value  # no cursor escape codes in the log


def test_no_animation_dedupes_dynamic_text():
    """A callback is logged once per *distinct* value, not once per frame."""
    steps: list[int] = []

    with capture() as stream:
        assert animate(counter(steps), text=lambda: f"step {len(steps)}/5", speed=0.005) == 5

    lines = stream.getvalue().splitlines()
    assert lines == sorted(set(lines), key=lines.index)  # no repeats
    assert lines[-1] == "step 5/5"
    assert len(lines) <= 6  # 'step 0/5' up to 'step 5/5'


def test_no_animation_constant_callback_logs_once():
    """A callback returning a constant behaves like static text."""
    with capture() as stream:
        animate(wait(1), text=lambda: "loading")

    assert stream.getvalue() == "loading\n"


def test_no_animation_clear_with():
    """clear_with marks completion on its own final line."""
    with capture() as stream:
        animate(wait(1), text="running", clear_with="✓")

    assert stream.getvalue() == "running\n✓ running\n"


def test_no_animation_without_text():
    """Nothing to say, nothing to log."""
    with capture() as stream:
        animate(wait(1))

    assert stream.getvalue() == ""


def test_force_animation():
    """force_animation overrides the terminal detection in both directions."""
    with capture(interactive=False) as stream:
        animate(wait(1), text="loading", force_animation=True)

    assert "\r" in stream.getvalue()  # animated despite not being a tty

    with capture(interactive=False) as stream:
        animate(wait(1), text="running", clear_with="✓", force_animation=True)

    assert stream.getvalue().endswith("✓ running\n\r")

    with capture(interactive=True) as stream:
        animate(wait(1), text="loading", force_animation=False)

    assert stream.getvalue() == "loading\n"  # not animated (and no cursor escapes) despite being a tty


def test_cursor_is_left_alone_when_not_a_terminal():
    """Escape codes would be garbage in a log file."""
    with capture() as stream:
        hide_cursor()
        show_cursor()
        with toggle_cursor(True):
            pass

    assert stream.getvalue() == ""

    with capture(interactive=True) as stream:
        hide_cursor()
        show_cursor()

    assert stream.getvalue() == "\033[?25l\033[?25h"
