import sys
from datetime import datetime

from threadful import animate, thread
from threadful.bonus import hide_cursor, toggle_cursor


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
